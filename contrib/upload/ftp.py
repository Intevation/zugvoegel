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
from datetime import datetime, timedelta


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

    # begin of campaign: older dates will not be considered
    TIMESTAMP_START = os.getenv("TIMESTAMP_START")
    TIMESTAMP_START_LATE = os.getenv("TIMESTAMP_START_LATE")
    # delay in days (current data will be ignored)
    TIMESTAMP_DELAY = int(os.getenv("TIMESTAMP_DELAY", '0'))
    # rule for sampling geo data (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html)
    # default '24H' means "sample every 24 hours", i.e. one day
    SAMPLE_RULE = os.getenv("SAMPLE_RULE", '24H')
    # Sampling can only create evenly distributed datapoints in time. So we use
    # another array to pick from those.
    # ATTENTION: SAMPLE_RULE must be set small enough such that the points that
    # are to be picked exist.
    SAMPLE_PICK = os.getenv("SAMPLE_PICK", '["00:00"]')
    COUNTRY_FILTER = os.getenv("COUNTRY_FILTER", '[]')

    ftp = None
    if FTP_HOST is not None and FTP_USER is not None and FTP_PASSWORD is not None and FTP_PATH is not None:
        ftp = FTP(FTP_HOST, FTP_USER, FTP_PASSWORD)
        ftp.cwd(FTP_PATH)

    # calculate end date (adding a delay to 'today')
    endtime = datetime.utcnow() - timedelta(days=TIMESTAMP_DELAY)
    endstring = str(endtime.year) + \
                str(endtime.month).zfill(2) + \
                str(endtime.day).zfill(2) + \
                str(endtime.hour).zfill(2) + \
                str(endtime.minute).zfill(2) + \
                "00000"

    # Convert json strings to data
    sample_pick = json.loads(SAMPLE_PICK)
    country_filter = json.loads(COUNTRY_FILTER)
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
            + "&timestamp_end=" + endstring
            + "&individual_id="
            + str(individual_id),
            auth=HTTPBasicAuth(MOVEBANK_USER, MOVEBANK_PASSWORD),
            verify=False,
        )
        # DEBUG: write movebank response data to file before processing
        # with open(FILE_OUT + '/' + bird + ".raw", 'w') as f:
        #     f.write(r.text)

        # Read csv
        df = pandas.read_csv(StringIO(r.text), index_col=0, parse_dates=True)
        if not df.empty:
            last = df.iloc[-1]
            if is_in_country(country_filter, last['location_lat'],last['location_long']):
                # clear all points
                df = df.iloc[0:0]
            else:
                # drop rows with empty fieds
                df.dropna(axis=0, inplace=True)
                # resampling cannot handle duplicates
                df.drop_duplicates(inplace=True)
                # make sure the resampling will reach until endtime by reinserting the last row at endtime
                df.loc[endtime] = list(df.iloc[-1])
                # movebank returns UTC timestamps
                df = df.tz_localize('utc').tz_convert('Europe/Berlin')
                # sample records down
                df = df.resample(SAMPLE_RULE).nearest().dropna(thresh=2)
                # resampling may introduce new duplicates in case there are big holes in the data
                df.drop_duplicates(inplace=True)
                # pick out desired data (SAMPLE_PICK)
                picked_df = []
                for t in sample_pick:
                    picked_df.append(df.at_time(t))
                df = pandas.concat(picked_df).sort_index()
                if df.empty:
                    logger.warn('No data could be sampled for ' + bird + '. Ensure SAMPLE_RULE provides enough data for SAMPLE_PICK')
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


def is_in_country(filter, lat, lon):
    if filter is None or len(filter) == 0:
        return False

    r = requests.get(
        "https://nominatim.openstreetmap.org/reverse?format=json" +
        "&lat=" + str(lat) + "&lon=" + str(lon),
        verify=False,
    )
    code = json.loads(r.text)['address']['country_code']
    return code in filter


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
