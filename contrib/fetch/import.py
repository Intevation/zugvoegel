
from dateutil import parser
from dotenv import load_dotenv
import json
import os
import psycopg
import sys


def _usage():
    me = sys.argv[0]
    usage_str = f"""
USAGE:
    python3 {me} [ journeys | individuals | locations ] <inputfile> [envfile]

Call {me} multiple times to import all data.
Order of imports to not violate constraints:
    1. individuals
    2. journeys
    3. locations
"""
    print(usage_str)


def _insert(conn, table, columns_str, values_str, values_tpl):
    sql = 'INSERT INTO ' + table + ' (' + columns_str + ') VALUES (' + values_str + ') RETURNING *;'
    r = conn.execute(sql, values_tpl).fetchone()
    print('INSERT INTO ' + table + ':', r)
    return r


def import_journeys(file, conn):
    input_json = json.load(file)

    # Check there is only one active journey
    found_active_journey = False
    for j in input_json:
        if j['active']:
            if found_active_journey:
                print('There can only be one active journey, please correct input.')
                print('Aborting...')
                return
            else:
                found_active_journey = True

    # Interactive key negotiation
    first_journey = dict(input_json[0])
    for k, v in first_journey.items():
        if type(v) == list and len(v) > 0:
            first_journey[k] = ['[shortened]']
        if type(v) == dict and len(v) > 0:
            first_journey[k] = {'[shortened]': '[shortened]'}
    print()
    print(json.dumps(first_journey, indent=4))
    print()
    print('Please have a look at the ([shortened]) first journey of your input above.')
    print('Now please tell me which json keys I should read for the DB-fields that are to be seeded.')
    print()
    journey_title_key = input('title  [title]: ') or 'title'
    journey_active_key = input('active  [active]: ') or 'active'
    journey_t_begin_key = input('t_begin  [t_begin]: ') or 't_begin'
    journey_t_end_key = input('t_end  [t_end]: ') or 't_end'
    journey_individuals_key = input('individuals  [turtledoves]: ') or 'turtledoves'

    first_individual = input_json[0][journey_individuals_key][0]
    print()
    print(json.dumps(first_individual, indent=4))
    print()
    print('Please have a look at the first individual of your input above.')
    print('Now please tell me which json keys I should read for the DB-fields that are to be seeded.')
    print()
    individual_active_key = input('active  [active]: ') or 'active'
    individual_local_identifier_key = input('individual_local_identifier  [individual_local_identifier]: ') or 'individual_local_identifier'

    print()
    if input('Start import? [y/N] ') not in ('y', 'Y'):
        print('Aborting...')
        return
    print()

    # Import loop
    for j in input_json:
        journey_title = j[journey_title_key]
        journey_active = j[journey_active_key]
        journey_t_begin = parser.parse(j[journey_t_begin_key])
        journey_t_end = parser.parse(j[journey_t_end_key])
        r = _insert(conn, 'journeys', 'title, active, t_begin, t_end', '%s, %s, %s, %s', (journey_title, journey_active, journey_t_begin, journey_t_end))
        journey_id = r[0]

        for i in j[journey_individuals_key]:
            individual_active = i[individual_active_key]
            individual_local_identifier = i[individual_local_identifier_key]

            sql = 'SELECT id FROM individuals WHERE individual_local_identifier=%s'
            r = conn.execute(sql, (individual_local_identifier,)).fetchone()
            if r is None:
                print(f'Individual {individual_local_identifier} could not be found DB.')
                print('Aborting...')
                return
            individual_id = r[0]

            r = _insert(conn, 'journeys_individuals', 'journey_id, individual_id, active', '%s, %s, %s', (journey_id, individual_id, individual_active))
            journeys_individuals_id = r[0]


def import_individuals(file, conn):
    input_json = json.load(file)
    
    # Interactive key negotiation
    print()
    print(json.dumps(input_json[0], indent=4))
    print()
    print('Please have a look at the first element of your input above.')
    print('Now please tell me which json keys I should read for the DB-fields that are to be seeded.')
    print()
    name_key = input('name  [name]: ') or 'name'
    individual_local_identifier_key = input('individual_local_identifier  [individual_local_identifier]: ') or 'individual_local_identifier'

    print()
    if input('Start import? [y/N] ') not in ('y', 'Y'):
        print('Aborting...')
        return
    print()

    # Import loop
    for i in input_json:
        name = i[name_key]
        individual_local_identifier = i[individual_local_identifier_key]
        r = _insert(conn, 'individuals', 'name, individual_local_identifier', '%s, %s', (name, individual_local_identifier))
        #individual_id = r[0]

def import_locations(file, conn):
    pass


def main():
    if len(sys.argv) < 3:
        _usage()
        sys.exit(1)

    if len(sys.argv) > 3:
        envfile = sys.argv[3]
    else:
        envfile = '.env'
    load_dotenv(dotenv_path=envfile)

    conn_args = {
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT'),
        'dbname': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD')
    }

    with open(sys.argv[2], 'r') as f:
        with psycopg.connect(**conn_args) as c:
            {
                'journeys': import_journeys,
                'individuals': import_individuals,
                'locations': import_locations
            }[sys.argv[1]](f, c)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("OUCH:", type(e).__name__)
        print(e)
        #raise e
        sys.exit(1)

