#!/usr/bin/env python3

import neo4j.v1
from lxml import etree


tree = etree.parse('intermine/genomic_model.xml')
model_package = tree.xpath('//model/@package')

terms_for_classes = {}

for _class in tree.xpath('//class'):
    attrib = _class.attrib

    if 'term' in attrib:
        terms_for_classes[model_package[0] + '.' + attrib['name']] = attrib['term']

"""
for k, v in terms_for_classes.items():
    print(k, v)
"""

with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
    with driver.session() as session:
        result = session.run("match (n {id:'b0005'}) return n")
        record = result.single()
        node = record['n']

        type = node['type']

        if type in terms_for_classes:
            _type = terms_for_classes[type]
        else:
            _type = None

        print(
            """@prefix sio: <http://semanticscience.org/resource/> .

<http://example-mine.org/ncbi:b0005>
  a %s .""" % _type)
