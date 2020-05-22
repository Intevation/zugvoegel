#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
load_dotenv()

FTP_HOST= os.getenv("FTP_HOST")
FTP_USER= os.getenv("FTP_USER")
FTP_PASSWORD=os.getenv("FTP_PASSWORD")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ftp = FTP(FTP_HOST,FTP_USER,FTP_PASSWORD)
ftp.cwd('turteltauben/data/turtledoves')

#storks = {'dana': 301885264, 'jan': 301885416, 'francesco': 301885945, 'nicola': 301885030}
storks = {'melanie': 894632438,'luciano': 900346098, 'cyril': 900348381, 'jenny': 900584891,'francesco': 301885945}

for stork,individual_id in storks.items():
    logger.info('PROCESSING: '+stork+'/'+str(individual_id))
    logger.info('Start reading '+stork+' from movebank.org')
    #Get csv data from movebank.org
    r = requests.get("https://www.movebank.org/movebank/service/direct-read?entity_type=event&attributes=timestamp,location_lat,location_long&study_id=301865163&timestamp_start=20190715000000000&individual_id="+str(individual_id), auth=HTTPBasicAuth('nabu-turteltaube', '20hama;Yiwe17'), verify=False)
    #Read csv
    df=pandas.read_csv(StringIO(r.text), index_col=0, parse_dates=True)
    #drop rows with empty fieds
    df.dropna(axis=0, inplace=True)
    #get only the last record of a day
    df=df.resample("D").last().dropna(thresh=2)
    #output
    output = StringIO()
    #export to csv
    df.to_csv(output)
    #Retrieve file content
    content = output.getvalue()
    # Close object and discard memory buffer --
    # .getvalue() will now raise an exception.
    output.close()
    #Create "csv file"
    csv_file = io.BytesIO(str.encode(content))
    #Store file on ftp
    logger.info('Store '+stork+' on ftp')
    ftp.storbinary('STOR '+stork+'2019_2020.csv', csv_file)

ftp.quit()
logger.info('Done')
