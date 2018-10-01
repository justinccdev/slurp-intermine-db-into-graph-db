#!/usr/bin/env python3

import argparse

import neo4j.v1
import psycopg2.extras

import sas.config_loaders
import sas.neo4j_pushers
import sas.intermine_data_loaders
import sas.intermine_model


intermine_to_neo4j_map = sas.config_loaders.load_intermine_to_neo4j_map('config/intermine_to_neo4j_map.json')
intermine_model = sas.intermine_model.InterMineModel('intermine/genomic_model.xml')

# If we are going to restrict the intermine entities that we map to neo4j, this is where we would do it
restrictions = {
    'Gene': set(),
    'Organism': set(),
    'Protein': set(),
    'SOTerm': set()
}

parser = argparse.ArgumentParser('Slurp InterMine data into Neo4J')
parser.add_argument('--limit', type=int, help='limit number of genes slurped if no gene id is specified')
parser.add_argument('gene', nargs='?')

args = parser.parse_args()

print(intermine_model.get_classes())

with \
    psycopg2.connect(dbname='synbiomine-v5-poc4', user='justincc', cursor_factory=psycopg2.extras.DictCursor) as conn, \
    neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver, \
        conn.cursor() as curs:

        if args.gene is not None:
            curs.execute('SELECT id FROM gene where secondaryidentifier=%s', (args.gene, ))
            restrictions['Gene'].add(str(curs.fetchone()['id']))
        elif args.limit is not None:
            cmd = 'SELECT id FROM gene LIMIT %d' % args.limit
            curs.execute(cmd)
            for row in curs:
                restrictions['Gene'].add(str(row['id']))

        if len(restrictions['Gene']) > 0:
            for referenced_type in intermine_model.get_classes():
                restrictions[referenced_type] \
                    = sas.intermine_data_loaders.get_referenced_im_ids(
                        curs, 'Gene', restrictions['Gene'], referenced_type, intermine_model)
                print('For %s got %s' % (referenced_type, restrictions[referenced_type]))

            print(restrictions)

        with driver.session() as session:
            for intermine_class in intermine_model.get_classes():
                sas.neo4j_pushers.add_entities(
                    session,
                    intermine_class,
                    sas.intermine_data_loaders.map_rows_to_dicts(
                        curs, intermine_class, intermine_to_neo4j_map, intermine_model, restrictions[intermine_class]))

            sas.neo4j_pushers.add_relationships(
                curs, session, 'Gene', intermine_model.get_classes(), intermine_model, restrictions['Gene'])
