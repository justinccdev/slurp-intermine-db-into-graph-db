#!/usr/bin/env python3

import neo4j.v1

with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
    with driver.session() as session:
        result = session.run("match (n {id:'b0005'}) return n")
        record = result.single()
        node = record['n']
        print(
            """<http://example-mine.org/ncbi:b0005>
  a '%s' .""" % node['type'])
