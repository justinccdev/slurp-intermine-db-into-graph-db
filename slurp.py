#!/usr/bin/env python3

import neo4j.v1
import psycopg2.extras


genes = {}
organisms = {}

conn = psycopg2.connect(dbname='synbiomine-v6', user='justincc', cursor_factory=psycopg2.extras.DictCursor)

with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
    with driver.session() as session:
        with conn.cursor() as curs:
            curs.execute("SELECT id, primaryidentifier, organismid, class FROM gene LIMIT 5")

            for row in curs:
                genes[row['id']] = {
                    'external_primary_id': row['primaryidentifier'],
                    'internal_organism_id': row['organismid'],
                    'type' : row['class']
                }

            for im_id, gene in genes.items():
                print(gene)
                session.run("CREATE (:gene { im_id:'%s', id:'%s', type:'%s' })" % (im_id, gene['external_primary_id'], gene['type']))

            curs.execute("SELECT id, taxonid, name, class FROM organism")

            for row in curs:
                organisms[row['id']] = { 'external_primary_id': row['taxonid'], 'name': row['name'], 'type': row['class'] }

            for im_id, organism in organisms.items():
                print(organism)
                session.run("CREATE (:organism { im_id:'%s', id:'%s', name: '%s', type:'%s' })" % (im_id, organism['external_primary_id'], organism['name'], organism['type']))

            for im_id, gene in genes.items():
                session.run("MATCH (g:gene {im_id:'%s'}), (o:organism {im_id:'%s'}) CREATE (g)-[:IN_GENOME_OF]->(o)" % (im_id, gene['internal_organism_id']))

conn.close()
