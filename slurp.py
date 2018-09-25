#!/usr/bin/env python3

import argparse
import json

import neo4j.v1
import psycopg2.extras

import sas.neo4j_pushers
import sas.intermine_data_loaders


# Map intermine columns to neo4j properties.
# Implicitly, we are doing
# { 'id': 'im_id',
#   'class': 'type }
# for everything
with open('config/intermine_to_neo4j_map.json') as f:
    intermine_to_neo4j_map = json.load(f)

print(intermine_to_neo4j_map)
for _map in intermine_to_neo4j_map['@maps'].values():
    _map.update(intermine_to_neo4j_map['@general'])

# If we are going to restrict the intermine entities that we map to neo4j, this is where we would do it
restrictions = {
    'gene': None,
    'organism': None,
    'protein': None,
    'soterm': None
}

parser = argparse.ArgumentParser('Slurp InterMine data into Neo4J')
# parser.add_argument('--limit', type=int, help='limit number of genes slurped for quicker testing')
parser.add_argument('gene', nargs='?')

args = parser.parse_args()

with \
    psycopg2.connect(dbname='synbiomine-v5-poc4', user='justincc', cursor_factory=psycopg2.extras.DictCursor) as conn, \
    neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver, \
    conn.cursor() as curs:
        # TODO: This is extremely crude and needs major refinement
        if args.gene is not None:
            curs.execute('SELECT * FROM gene where secondaryidentifier=%s', (args.gene, ))
            restrictions['gene'] = [str(curs.fetchone()['id'])]

            restrictions['protein'] = []
            for im_id in restrictions['gene']:
                curs.execute('SELECT proteins FROM genesproteins WHERE genes=%s', (im_id,))
                for row in curs:
                    restrictions['protein'].append(str(row['proteins']))

            restrictions['organism'] = []
            restrictions['soterm'] = []

            print(restrictions)

        with driver.session() as session:
            for intermine_class, _map in intermine_to_neo4j_map['@maps'].items():
                 sas.neo4j_pushers.add_entities(
                     session,
                     intermine_class,
                     sas.intermine_data_loaders.map_rows_to_dicts(
                         curs, intermine_class, _map, restrictions[intermine_class]))

            sas.neo4j_pushers.add_relationships(curs, session, restrictions['gene'])
