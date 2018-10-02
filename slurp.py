#!/usr/bin/env python3

import argparse

import neo4j.v1
import psycopg2.extras

import sas.config_loaders
import sas.intermine_data_loaders
import sas.intermine_model
import sas.neo4j_pushers
import sas.slurp


intermine_to_neo4j_map = sas.config_loaders.load_intermine_to_neo4j_map('config/intermine_to_neo4j_map.json')
intermine_model = sas.intermine_model.InterMineModel('intermine/genomic_model.xml')

parser = argparse.ArgumentParser('Slurp InterMine data into Neo4J')
parser.add_argument('--depth', type=int, help='number of links to follow when slurping')
parser.add_argument('--limit', type=int, help='limit number of genes slurped if no gene id is specified')
parser.add_argument('gene', nargs='?')

args = parser.parse_args()

with \
    psycopg2.connect(dbname='synbiomine-v5-poc4', user='justincc', cursor_factory=psycopg2.extras.DictCursor) as conn, \
    neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd'), max_retry_time=60) as driver, \
        conn.cursor() as curs:

        if args.gene or args.limit:
            selections = {source_class: set() for source_class in intermine_model.get_classes()}
        else:
            selections = None

        if args.gene:
            curs.execute('SELECT id FROM gene where secondaryidentifier=%s', (args.gene, ))
            selections['Gene'] = {str(curs.fetchone()['id'])}
        elif args.limit:
            cmd = 'SELECT id FROM gene LIMIT %d' % args.limit
            curs.execute(cmd)
            for row in curs:
                selections['Gene'].add(str(row['id']))

        depth = args.depth if args.depth else 1

        if selections:
            for i in range(depth):
                print('************ ROUND %d' % i)
                for source_class, ids in selections.copy().items():
                    if len(ids) > 0:
                        for referenced_class in intermine_model.get_classes():
                            if referenced_class == 'BioEntity':
                                continue

                            referenced_im_ids = sas.intermine_data_loaders.get_referenced_im_ids(
                                curs, source_class, ids, referenced_class, intermine_model)

                            selections[referenced_class] = selections[referenced_class].union(referenced_im_ids)

                sas.slurp.print_selections_counts(selections)

        with driver.session() as session:
            for intermine_class in intermine_model.get_classes():
                entities = sas.intermine_data_loaders.map_rows_to_dicts(
                    curs,
                    intermine_class,
                    intermine_to_neo4j_map,
                    intermine_model,
                    selections[intermine_class] if selections else None)

                sas.neo4j_pushers.add_entities(session, intermine_class, entities)

            for intermine_class, selection in selections.items():
                if len(selection) <= 0:
                    continue

                # FIXME: We need to specifically exclude these relationships for now as they connect to every BioEntity in
                # the system which is a huge performance hog (probably can be improved by collecting all the leaf IDs
                # we are referencing and using those to restrict the relationships from postgres that we look at
                if intermine_class == 'DataSet' or intermine_class == 'Publication':
                    continue

                print('Adding relationships for %s' % intermine_class)
                sas.neo4j_pushers.add_relationships(
                    curs,
                    session,
                    intermine_class,
                    intermine_model.get_classes(),
                    intermine_model,
                    selection)

            print('Finishing up')
