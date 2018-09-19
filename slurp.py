#!/usr/bin/env python3

import neo4j.v1
import psycopg2.extras
import slurp.adders
import slurp.slurpers


with psycopg2.connect(dbname='synbiomine-v6', user='justincc', cursor_factory=psycopg2.extras.DictCursor) as conn:
    with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
        with driver.session() as session:
            with conn.cursor() as curs:
                genes = slurp.slurpers.get_im_genes(curs)
                slurp.adders.add_genes(session, genes)
                slurp.adders.add_organisms(session, slurp.slurpers.get_im_organisms(curs))
                slurp.adders.add_relationships(session, genes)
