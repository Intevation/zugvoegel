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
from datetime import date, timedelta


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
    TIMESTAMP_DELAY = int(os.getenv("TIMESTAMP_DELAY", "0"))
    # rule for sampling geo data (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html)
    # default '1D' means "sample every one day"
    # '0.5D' means "sample every half day", i.e. twice a day
    SAMPLE_RULE = os.getenv("SAMPLE_RULE", "1D")

    ftp = None
    if FTP_HOST is not None and FTP_USER is not None and FTP_PASSWORD is not None and FTP_PATH is not None:
        ftp = FTP(FTP_HOST, FTP_USER, FTP_PASSWORD)
        ftp.cwd(FTP_PATH)

    # calculate end date (adding a delay to 'today')
    enddate = date.today() - timedelta(days=TIMESTAMP_DELAY)
    endstring = str(enddate.year) + str(enddate.month).zfill(2) + str(enddate.day).zfill(2) + "000000000"

    # Convert dictionary string to dictionary
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
            # drop rows with empty fieds
            df.dropna(axis=0, inplace=True)
            df.drop_duplicates(inplace=True)
            # sample records down
            df = df.resample(SAMPLE_RULE).nearest().dropna(thresh=2)
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
