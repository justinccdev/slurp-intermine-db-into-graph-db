#!/usr/bin/env python3

import neo4j.v1
import psycopg2.extras


genes = {}
organisms = {}

conn = psycopg2.connect(dbname='synbiomine-v6', user='justincc', cursor_factory=psycopg2.extras.DictCursor)

with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
    with driver.session() as session:
        with conn.cursor() as curs:
            curs.execute("SELECT id, primaryidentifier, class FROM gene")

            for row in curs:
                genes[row['id']] = { 'external_primary_id': row['primaryidentifier'], 'type' : row['class'] }

            for gene in genes.values():
                print(gene)
                session.run("CREATE (:gene { id:'%s', type:'%s' })" % (gene['external_primary_id'], gene['type']))

            curs.execute("SELECT id, taxonid, name, class FROM organism")

            for row in curs:
                organisms[row['id']] = { 'external_primary_id': row['taxonid'], 'name': row['name'], 'type': row['class'] }

            for organism in organisms.values():
                print(organism)
                session.run("CREATE (:organism { id:'%s', name: '%s', type:'%s' })" % (id, name, type))

conn.close()
