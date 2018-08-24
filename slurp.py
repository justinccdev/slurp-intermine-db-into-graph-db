#!/usr/bin/env python3

import psycopg2.extras

conn = psycopg2.connect(dbname='synbiomine-v6', user='justincc', cursor_factory=psycopg2.extras.DictCursor)

with conn.cursor() as curs:
    curs.execute("SELECT primaryidentifier, class FROM gene WHERE primaryIdentifier='b0001'")
    row = curs.fetchone()
    print(row['primaryidentifier'], row['class'])

conn.close()
