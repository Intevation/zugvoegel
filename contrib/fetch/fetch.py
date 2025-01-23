
import sys
import os

import datetime
from dateutil import parser
from dotenv import load_dotenv
import json
import logging
import psycopg
import requests
from requests.auth import HTTPBasicAuth


env = {}
pg_conn_args = {}
logger = None


SCHEMA = """
CREATE TABLE IF NOT EXISTS journeys (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    active BOOL NOT NULL,
    title TEXT NOT NULL,
    last_update TIMESTAMP,
    t_begin TIMESTAMP,
    t_end TIMESTAMP
);
-- Only one journey may be active.
-- -> Create partial unique index on all rows where active is true
CREATE UNIQUE INDEX only_one_active_journey_uix 
    ON journeys (active) WHERE (active);

CREATE TABLE IF NOT EXISTS individuals (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL,
    individual_local_identifier TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS journeys_individuals (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    journey_id INTEGER REFERENCES journeys(id) NOT NULL,
    individual_id INTEGER REFERENCES individuals(id) NOT NULL,
    active BOOL NOT NULL
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    journeys_individuals_id INTEGER REFERENCES journeys_individuals(id) NOT NULL,
    timestamp TIMESTAMP UNIQUE NOT NULL,
    location_long REAL NOT NULL,
    location_lat REAL NOT NULL
);
"""


# https://github.com/movebank/movebank-api-doc/blob/master/movebank-api.md#get-json-event-data-for-a-specified-time-period
#   The timestamps must be provided in milliseconds since 1970-01-01.
#   All dates in Movebank are stored in UTC.

def to_movebank_timestamp(t):
    return str(int(t.timestamp() * 1000.0 ))

def from_movebank_timestamp(t):
    return datetime.datetime.fromtimestamp(int(float(t) / 1000.0), datetime.UTC)

def response_from_movebank_timestamp(r):
    for i in range(len(r['individuals'])):
        for l in range(len(r['individuals'][i]['locations'])):
            t = from_movebank_timestamp(r['individuals'][i]['locations'][l]['timestamp'])
            r['individuals'][i]['locations'][l]['timestamp'] = t


def fetch_from_movebank():
    sensortypestring = ""
    if env['SENSOR_TYPE'] is not None:
        sensortypestring = "&sensor_type=" + env['SENSOR_TYPE']

    data = { 'individuals' : [] }
    for individual_local_identifier in env['INDIVIDUALS']:
        url = "https://www.movebank.org/movebank/service/json-auth" \
            + "?study_id=" + env['STUDY_ID'] \
            + "&individual_local_identifiers=" + individual_local_identifier \
            + sensortypestring \
            + "&timestamp_start=" + to_movebank_timestamp(env['TIMESTAMP_START'])
            #+ endstring

        logger.info("requests.get " + url)

        response = requests.get(url, auth=HTTPBasicAuth(env['MOVEBANK_USER'], env['MOVEBANK_PASSWORD']))
        if 200 <= response.status_code < 300:
            data['individuals'].extend(json.loads(response.text)['individuals'])
        else:
            logger.error("Response Code not 2XX")

    response_from_movebank_timestamp(data)

    return data


def apply_schema():
    with psycopg.connect(**pg_conn_args) as conn:
        conn.execute(SCHEMA)


def store_to_db(movebank_data):
    #for i in movebank_data['individuals']:
    #    #ggjj
    #    pass
    pass


def init_env():
    global env

    # env file selection
    if len(sys.argv) > 1:
        envfile = sys.argv[1]
    else:
        envfile = '.env'
    load_dotenv(dotenv_path=envfile)

    # general
    env['LOG_LEVEL'] = os.getenv("LOG_LEVEL", 'INFO')

    # movebank credentials
    env['MOVEBANK_USER'] = os.getenv("MOVEBANK_USER")
    env['MOVEBANK_PASSWORD'] = os.getenv("MOVEBANK_PASSWORD")

    # movebank settings
    env['STUDY_ID'] = os.getenv("STUDY_ID")
    env['SENSOR_TYPE_ID'] = os.getenv("SENSOR_TYPE_ID")
    if env['SENSOR_TYPE_ID'] is not None:
        logger.warn('SENSOR_TYPE_ID is no longer considered by this tool.')
        logger.warn('If you are setting it to 653, instead set SENSOR_TYPE=gps')
    env['SENSOR_TYPE'] = os.getenv("SENSOR_TYPE")
    env['INDIVIDUALS'] = json.loads(os.getenv("INDIVIDUALS"))
    env['TIMESTAMP_START'] = parser.parse(os.getenv("TIMESTAMP_START"))

    # pg credentials
    env['POSTGRES_HOST'] = os.getenv("POSTGRES_HOST")
    env['POSTGRES_PORT'] = os.getenv("POSTGRES_PORT")
    env['POSTGRES_DB'] = os.getenv("POSTGRES_DB")
    env['POSTGRES_USER'] = os.getenv("POSTGRES_USER")
    env['POSTGRES_PASSWORD'] = os.getenv("POSTGRES_PASSWORD")


def init_logger():
    global logger

    level = logging.getLevelNamesMapping()[env['LOG_LEVEL']]
    logging.basicConfig(level=level)
    logger = logging.getLogger(__name__)


def init_pg_conn_args():
    global pg_conn_args

    pg_conn_args = {
        'host': env['POSTGRES_HOST'],
        'port': env['POSTGRES_PORT'],
        'dbname': env['POSTGRES_DB'],
        'user': env['POSTGRES_USER'],
        'password': env['POSTGRES_PASSWORD']
    }
    logger.debug('postgres conn_args: ' + str(pg_conn_args | { 'password': '***' }))


def main():
    init_env()
    init_logger()
    init_pg_conn_args()

    #apply_schema()

    data = fetch_from_movebank()
    print(json.dumps(data, default=str))
    #store_to_db([])


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.fatal("OUCH: " + type(e).__name__)
        logger.fatal(repr(e))
        #raise e
        sys.exit(1)

