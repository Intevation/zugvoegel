#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import requests
from requests.auth import HTTPBasicAuth
import logging
from ftplib import FTP
from io import StringIO
import io
import pandas
import urllib3
from datetime import datetime, timedelta, date


urllib3.disable_warnings()
import os
from dotenv import load_dotenv
from typing import List

USAGE = "Usage: python {} [--help] | filename]".format(sys.argv[0])


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def validate(args: List[str]):
    filename = args[0]
    load_dotenv(dotenv_path=filename)
    # output FTP server settings
    FTP_HOST = os.getenv("FTP_HOST")
    FTP_USER = os.getenv("FTP_USER")
    FTP_PASSWORD = os.getenv("FTP_PASSWORD")
    FTP_PATH = os.getenv("FTP_PATH")
    FILE_OUT = os.getenv("FILE_OUT")
    CSV_FILE_POSTFIX = os.getenv("CSV_FILE_POSTFIX")

    # movebank settings
    STUDY_ID = os.getenv("STUDY_ID")
    MOVEBANK_USER = os.getenv("MOVEBANK_USER")
    MOVEBANK_PASSWORD = os.getenv("MOVEBANK_PASSWORD")

    # list of birds considered: json object with name: movebank_identifier
    BIRDS = os.getenv("BIRDS")
    SENSOR_TYPE_ID = os.getenv("SENSOR_TYPE_ID")

    # begin of campaign: older dates will not be considered
    TIMESTAMP_START = os.getenv("TIMESTAMP_START")
    TIMESTAMP_START_LATE = os.getenv("TIMESTAMP_START_LATE")
    TIMESTAMP_END = os.getenv("TIMESTAMP_END", None)
    # delay in days (current data will be ignored)
    TIMESTAMP_DELAY = int(os.getenv("TIMESTAMP_DELAY", '0'))
    # rule for sampling geo data (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html)
    # default '24H' means "sample every 24 hours", i.e. one day
    SAMPLE_RULE = os.getenv("SAMPLE_RULE", "24h")
    # Sampling can only create evenly distributed datapoints in time. So we use
    # another array to pick from those.
    # ATTENTION: SAMPLE_RULE must be set small enough such that the points that
    # are to be picked exist.
    SAMPLE_PICK = os.getenv("SAMPLE_PICK", '["00:00"]')
    FILTER_RECTANGLES = os.getenv("FILTER_RECTANGLES", '[]')

    LOG_LAST_N = int(os.getenv("LOG_LAST_N", '3'))

    ftp = None
    if FTP_HOST is not None and FTP_USER is not None and FTP_PASSWORD is not None and FTP_PATH is not None:
        ftp = FTP(FTP_HOST, FTP_USER, FTP_PASSWORD)
        ftp.cwd(FTP_PATH)

    # calculate end date (adding a delay to 'today')
    endtime = datetime.utcnow() - timedelta(days=TIMESTAMP_DELAY)

    if TIMESTAMP_END is not None:
        envendtime = datetime(
                        int(TIMESTAMP_END[:4]),      # year
                        int(TIMESTAMP_END[4:6]),     # month
                        int(TIMESTAMP_END[6:8]),     # day
                        int(TIMESTAMP_END[8:10]),    # hour
                        int(TIMESTAMP_END[10:12])    # minute
                    ) - timedelta(days=TIMESTAMP_DELAY)
        if endtime > envendtime:
            endtime = envendtime

    endtimestamp =  str(endtime.year) + \
                    str(endtime.month).zfill(2) + \
                    str(endtime.day).zfill(2) + \
                    str(endtime.hour).zfill(2) + \
                    str(endtime.minute).zfill(2) + \
                    "00000"

    endstring = "&timestamp_end=" + \
                endtimestamp
    
    sensortypestring = ""
    if SENSOR_TYPE_ID is not None:
        sensortypestring = "&sensor_type_id=" + SENSOR_TYPE_ID

    # Convert json strings to data
    sample_pick = json.loads(SAMPLE_PICK)
    filter_rectangles = json.loads(FILTER_RECTANGLES)
    birds = json.loads(BIRDS)
    for bird, individual_id in birds.items():
        if bird in ['051T', '052T']: # special handling for late birds
            times = TIMESTAMP_START_LATE
        else:
            times = TIMESTAMP_START
        logger.info("PROCESSING: " + bird + "/" + str(individual_id))
        logger.info("Start reading " + bird + " from movebank.org")
        # Get csv data from movebank.org
        r = requests.get(
            "https://www.movebank.org/movebank/service/direct-read?entity_type=event&attributes=timestamp,location_lat,location_long,visible&study_id="
            + STUDY_ID
            + "&timestamp_start="
            + times
            + endstring
            + "&individual_id="
            + str(individual_id)
            # handle with caution, 
            + sensortypestring
            ,
            auth=HTTPBasicAuth(MOVEBANK_USER, MOVEBANK_PASSWORD),
            verify=False,
        )
        # DEBUG: write movebank response data to file before processing
        # with open(FILE_OUT + '/' + bird + ".raw", 'w') as f:
        #     f.write(r.text)

        # Read csv
        df = pandas.read_csv(StringIO(r.text), index_col=0, parse_dates=True)
        do_filtering = False
        if not df.empty:
            log_last_n(LOG_LAST_N, df, " returned by movebank")

            # pandas DataFrame operations
            # drop rows with empty fieds
            df.dropna(axis=0, inplace=True)
            last = df.iloc[-1]
            if is_in_filter_rectangles(filter_rectangles, last['location_lat'],last['location_long']):
                # clear all points within the filter rectangles later
                do_filtering = True
                logger.info(bird + " was last seen in one of the filter rectangles. Filtering out points ...")
            # resampling cannot handle duplicates
            # df.drop_duplicates(inplace=True) doesn't work in this DataFrame because it's a DateTimeIndex
            df = df[~df.index.duplicated(keep='first')]
            # make sure the resampling will reach until endtime by reinserting the last row at endtime
            # -> but only if last location was recorded within the last day.
            days_since = (date.today() - df.tail(1).index[0].date()).days
            if days_since < 1:
                df.loc[endtime] = list(df.iloc[-1])
            # movebank returns UTC timestamps
            df = df.tz_localize('utc').tz_convert('Europe/Berlin')
            # sample records down
            df = df.resample(SAMPLE_RULE).nearest().dropna(thresh=2)



            # pick out desired data (SAMPLE_PICK)
            picked_df = []
            for t in sample_pick:
                picked_df.append(df.at_time(t))
            df = pandas.concat(picked_df).sort_index()
            if df.empty:
                logger.warn('No data could be sampled for ' + bird + '. Ensure SAMPLE_RULE provides enough data for SAMPLE_PICK')
            if do_filtering:
                df = df.apply(lambda x:
                    None if
                    is_in_filter_rectangles(filter_rectangles, x['location_lat'], x['location_long'])
                    else x, axis=1, result_type='broadcast')
            df.dropna(axis=0, inplace=True)
            log_last_n(LOG_LAST_N, df, " after processing")
        # output
        output = StringIO()
        # export to csv
        df.to_csv(output)
        # Retrieve file content
        content = output.getvalue()
        # Close object and discard memory buffer --
        # .getvalue() will now raise an exception.
        output.close()
        # Create "csv file"
        csv_file = io.BytesIO(str.encode(content))
        # Store file on ftp
        if ftp is not None:
            ftp.storbinary("STOR " + bird + CSV_FILE_POSTFIX, csv_file)
            logger.info(
                "Stored "
                + bird
                + CSV_FILE_POSTFIX
                + " on ftp://"
                + FTP_USER
                + ":PASSWORD@"
                + FTP_HOST
                + "/"
                + FTP_PATH
            )
        if FILE_OUT is not None:
            with open(FILE_OUT + '/' + bird + CSV_FILE_POSTFIX, 'w') as f:
                f.write(content)
                logger.info("Saved file " + FILE_OUT + '/' + bird + CSV_FILE_POSTFIX)
        logger.info("-----------------")
    if ftp is not None:
        ftp.quit()
    logger.info("Done")

def is_in_filter_rectangles(filter, lat, lon):
    if filter is None or len(filter) == 0:
        return False

    for rect in filter:
        topleft = rect[0]
        botright = rect[1]

        if lat < topleft[0] and \
           lon > topleft[1] and \
           lat > botright[0] and \
           lon < botright[1]:
            return True

    return False


def log_last_n(n, df, s):
    if n > 0:
        logger.info("Last " + str(n) + " locations" + s + ": ")
        for i in reversed(range(n)):
            d = df.iloc[-1 - i]
            logger.info("  #(N-" + str(i) + "): " +
                str(d.name or "name:error") +
                " (lat: " + str(d["location_lat"] or "lat:error") +
                " ,lon: " + str(d["location_long"] or "lon:error") + ")")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        raise SystemExit(USAGE)

    if args[0] == "--help":
        print(USAGE)
    else:
        validate(args)


if __name__ == "__main__":
    main()
