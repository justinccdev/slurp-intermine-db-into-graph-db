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
prefixes_used = set()
subjects = {}

with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
    with driver.session() as session:
        result = session.run("match (n {id:'%s'}) return n" % args.id)
        record = result.single()
        node = record['n']

        for key, value in node.items():
            if key == 'type':
                slurp.rdf_creators.process_class_type(
                    value, terms_for_classes, prefixes, prefixes_used, subjects, args.id)
            if key == 'symbol':
                slurp.rdf_creators.process_symbol(
                    value, terms_for_classes, prefixes, prefixes_used, subjects, args.id)

for prefix_used in prefixes_used:
    print('@prefix %s: <%s/> .' % (prefix_used, prefixes[prefix_used]))

print()

for s, po in subjects.items():
    p, o = po

    print('<%s>' % s)

    p = slurp.rdf_creators.get_rdf_for_triple_part(p, prefixes)
    o = slurp.rdf_creators.get_rdf_for_triple_part(o, prefixes)

    print('  %s %s .' % (p, o))
