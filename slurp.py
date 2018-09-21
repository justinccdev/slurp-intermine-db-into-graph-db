#!/usr/bin/env python3

import neo4j.v1
import psycopg2.extras
import sas.adders
import sas.slurpers


with psycopg2.connect(dbname='synbiomine-v6', user='justincc', cursor_factory=psycopg2.extras.DictCursor) as conn:
    with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
        with driver.session() as session:
            with conn.cursor() as curs:
                genes = sas.slurpers.get_im_genes(curs)
                sas.adders.add_genes(session, genes)
                sas.adders.add_organisms(session, sas.slurpers.get_im_organisms(curs))
                sas.adders.add_relationships(session, genes)
