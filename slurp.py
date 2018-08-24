#!/usr/bin/env python3

import neo4j.v1
import psycopg2.extras

conn = psycopg2.connect(dbname='synbiomine-v6', user='justincc', cursor_factory=psycopg2.extras.DictCursor)

with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
    with driver.session() as session:
        with conn.cursor() as curs:
            curs.execute("SELECT primaryidentifier, class FROM gene")

            for row in curs:
                id, type = row
                print(id, type)
                session.run("CREATE (:gene { id:'%s', type:'%s' })" % (id, type))

            curs.execute("SELECT taxonid, name, class FROM organism")

            for row in curs:
                id, name, type = row
                print(id, name, type)
                session.run("CREATE (:organism { id:'%s', name: '%s', type:'%s' })" % (id, name, type))

conn.close()
