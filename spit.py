#!/usr/bin/env python3

import argparse

import neo4j.v1
import slurp.rdf_creators
import slurp.spitters

parser = argparse.ArgumentParser('Spit out RDF for a given gene ID (try EG11277)')
parser.add_argument('id', help='Gene ID')
args = parser.parse_args()

prefixes = slurp.spitters.load_rdf_prefixes('config/rdf-prefixes.xml')
terms_for_classes = slurp.spitters.load_terms('intermine/genomic_model.xml')
extensions_used = set()
nodes = {}

with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
    with driver.session() as session:
        result = session.run("match (n {id:'%s'}) return n" % args.id)
        record = result.single()
        node = record['n']

        class_type = node['type']

        if class_type in terms_for_classes:
            term = terms_for_classes[class_type]
        else:
            term = None

        prefix = slurp.rdf_creators.find_rdf_prefix_if_available(term, prefixes)
        if prefix is not None:
            extensions_used.add(prefix)

        nodes[slurp.rdf_creators.create_node_subject(args.id)] = term

for extension_used in extensions_used:
    prefix = prefixes[extension_used]
    print('@prefix %s: <%s/> .' % (prefix, extension_used))

print()

for k, v in nodes.items():
    print('<%s>' % k)
    print('  a <%s> .' % v)
