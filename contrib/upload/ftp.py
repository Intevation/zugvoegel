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

urllib3.disable_warnings()
import os
from dotenv import load_dotenv
from typing import List

USAGE = f"Usage: python {sys.argv[0]} [--help] | filename]"


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def validate(args: List[str]):
    filename = args[0]
    load_dotenv(dotenv_path=filename)
    FTP_HOST = os.getenv("FTP_HOST")
    FTP_USER = os.getenv("FTP_USER")
    FTP_PASSWORD = os.getenv("FTP_PASSWORD")
    FTP_PATH = os.getenv("FTP_PATH")
    STUDY_ID = os.getenv("STUDY_ID")
    BIRDS = os.getenv("BIRDS")
    TIMESTAMP_START = os.getenv("TIMESTAMP_START")
    MOVEBANK_USER = os.getenv("MOVEBANK_USER")
    MOVEBANK_PASSWORD = os.getenv("MOVEBANK_PASSWORD")
    CSV_FILE_POSTFIX = os.getenv("CSV_FILE_POSTFIX")
    ftp = FTP(FTP_HOST, FTP_USER, FTP_PASSWORD)
    ftp.cwd(FTP_PATH)

    # Convert dictionary string to dictionary
    birds = json.loads(BIRDS)
    for bird, individual_id in birds.items():
        logger.info("PROCESSING: " + bird + "/" + str(individual_id))
        logger.info("Start reading " + bird + " from movebank.org")
        # Get csv data from movebank.org
        r = requests.get(
            "https://www.movebank.org/movebank/service/direct-read?entity_type=event&attributes=timestamp,location_lat,location_long&study_id="
            + STUDY_ID
            + "&timestamp_start="
            + TIMESTAMP_START
            + "&individual_id="
            + str(individual_id),
            auth=HTTPBasicAuth(MOVEBANK_USER, MOVEBANK_PASSWORD),
            verify=False,
        )
        # Read csv
        df = pandas.read_csv(StringIO(r.text), index_col=0, parse_dates=True)
        # drop rows with empty fieds
        df.dropna(axis=0, inplace=True)
        # get only the last record of a day
        df = df.resample("D").last().dropna(thresh=2)
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
        logger.info(
            "Store "
            + bird
            + CSV_FILE_POSTFIX
            + " on ftp://"
            + FTP_USER
            + ":PASSWORD@"
            + FTP_HOST
            + "/"
            + FTP_PATH
        )
        ftp.storbinary("STOR " + bird + CSV_FILE_POSTFIX, csv_file)
        logger.info("-----------------")
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
