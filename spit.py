#!/usr/bin/env python3

import argparse

import neo4j.v1
import slurp.spitters

parser = argparse.ArgumentParser('Spit out RDF for a given gene ID (try EG11277)')
parser.add_argument('id', help='Gene ID')
args = parser.parse_args()

prefixes = slurp.spitters.load_rdf_prefixes('config/rdf-prefixes.xml')
terms_for_classes = slurp.spitters.get_terms_for_classes('intermine/genomic_model.xml')
extensions_used = set()
nodes = {}

with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
    with driver.session() as session:
        result = session.run("match (n {id:'%s'}) return n" % args.id)
        record = result.single()
        node = record['n']

        class_type = node['type']

        if class_type in terms_for_classes:
            _type = terms_for_classes[class_type]
        else:
            _type = None

        resource = _type.rpartition('/')[0]
        if resource in prefixes:
            extensions_used.add(resource)

        nodes['http://synbiomine.org/ncbi:%s' % args.id] = _type

for extension_used in extensions_used:
    prefix = prefixes[extension_used]
    print('@prefix %s: <%s/> .' % (prefix, extension_used))

print()

for k, v in nodes.items():
    print('<%s>' % k)
    print('  a <%s> .' % v)
