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

parser = argparse.ArgumentParser('Slurp InterMine data into Neo4J')
parser.add_argument('--depth', type=int, help='number of links to follow when slurping')
parser.add_argument('--limit', type=int, help='limit number of genes slurped if no gene id is specified')
parser.add_argument('gene', nargs='?')

args = parser.parse_args()

with \
    psycopg2.connect(dbname='synbiomine-v5-poc4', user='justincc', cursor_factory=psycopg2.extras.DictCursor) as conn, \
    neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver, \
        conn.cursor() as curs:

        restrictions = {source_class:set() for source_class in intermine_model.get_classes()}

        if args.gene is not None:
            curs.execute('SELECT id FROM gene where secondaryidentifier=%s', (args.gene, ))
            restrictions['Gene'].add(str(curs.fetchone()['id']))
        elif args.limit is not None:
            cmd = 'SELECT id FROM gene LIMIT %d' % args.limit
            curs.execute(cmd)
            for row in curs:
                restrictions['Gene'].add(str(row['id']))

        depth = args.depth if args.depth else 1

        for i in range(depth):
            print('************ ROUND %d' % i)
            for source_class, ids in restrictions.copy().items():
                if len(ids) > 0:
                    for referenced_class in intermine_model.get_classes():
                        referenced_im_ids = sas.intermine_data_loaders.get_referenced_im_ids(
                            curs, source_class, ids, referenced_class, intermine_model)

                        restrictions[referenced_class] = restrictions[referenced_class].union(referenced_im_ids)

            count = 0
            for referenced_class in filter(lambda c: len(restrictions[c]) > 0, restrictions.keys()):
                n = len(restrictions[referenced_class])
                count += n
                print('For %s got %d restrictions' % (referenced_class, n))

            print('Got %d total restrictions' % count)

        with driver.session() as session:
            for intermine_class in intermine_model.get_classes():
                sas.neo4j_pushers.add_entities(
                    session,
                    intermine_class,
                    sas.intermine_data_loaders.map_rows_to_dicts(
                        curs, intermine_class,
                        intermine_to_neo4j_map, intermine_model, restrictions.get(intermine_class)))

            # for intermine_class in intermine_model.get_classes():
            # for intermine_class in 'Gene',:
            for intermine_class in restrictions:
                # We need to specifically exclude this for now as DataSets connect to every BioEntity in the system
                if intermine_class == 'DataSet':
                    continue

                print('Adding relationships for %s' % intermine_class)
                sas.neo4j_pushers.add_relationships(
                    curs, session, intermine_class, intermine_model.get_classes(),
                    intermine_model, restrictions[intermine_class])
