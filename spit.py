#!/usr/bin/env python3

import neo4j.v1
import slurp.spitters


terms_for_classes = slurp.spitters.get_terms_for_classes('intermine/genomic_model.xml')

with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
    with driver.session() as session:
        result = session.run("match (n {id:'b0005'}) return n")
        record = result.single()
        node = record['n']

        class_type = node['type']

        if class_type in terms_for_classes:
            _type = terms_for_classes[class_type]
        else:
            _type = None

        print(
            """@prefix sio: <http://semanticscience.org/resource/> .

<http://example-mine.org/ncbi:b0005>
  a %s .""" % _type)
