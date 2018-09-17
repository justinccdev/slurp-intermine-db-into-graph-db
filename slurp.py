#!/usr/bin/env python3

import neo4j.v1
import psycopg2.extras
import sid.adders
import sid.slurpers


conn = psycopg2.connect(dbname='synbiomine-v6', user='justincc', cursor_factory=psycopg2.extras.DictCursor)

with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
    with driver.session() as session:
        with conn.cursor() as curs:
            genes = sid.slurpers.get_im_genes(curs)
            sid.adders.add_genes(session, genes)
            sid.adders.add_organisms(session, sid.slurpers.get_im_organisms(curs))
            sid.adders.add_relationships(session, genes)

conn.close()
