#!/usr/bin/env python3

import neo4j.v1
import psycopg2.extras
import sas.neo4j_pushers
import sas.intermine_data_loaders


with psycopg2.connect(dbname='synbiomine-v6', user='justincc', cursor_factory=psycopg2.extras.DictCursor) as conn:
    with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
        with driver.session() as session:
            with conn.cursor() as curs:
                genes = sas.intermine_data_loaders.get_im_genes(curs)
                sas.neo4j_pushers.add_entities(session, 'gene', genes)
                sas.neo4j_pushers.add_entities(session, 'organism', sas.intermine_data_loaders.get_im_organisms(curs))
                sas.neo4j_pushers.add_relationships(session, genes)
