#!/usr/bin/env python3

import argparse

import neo4j.v1
import slurp.rdf_creators
import slurp.spitters

parser = argparse.ArgumentParser('Spit out RDF for a given gene ID (try EG11277)')
parser.add_argument('id', help='Gene ID')
args = parser.parse_args()

prefixes = slurp.spitters.load_rdf_prefixes('config/rdf-prefixes.xml')
model_terms = slurp.spitters.load_terms('intermine/genomic_model.xml')
prefixes_used = set()
subjects = {}

with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
    with driver.session() as session:
        result = session.run("match (n {id:'%s'}) return n" % args.id)
        record = result.single()
        node = record['n']

        subject_name = slurp.rdf_creators.create_node_subject(args.id)
        pos = []
        subjects[subject_name] = pos

        node_type = node['type'].rpartition('.')[2]

        for key, value in node.items():
            # print('KEY-VALUE: %s,%s' % (key, value))
            term = p = o = None

            if key == 'type':
                term = model_terms.get(node_type)
                p, o = 'a', term

            else:
                term = model_terms.get('%s.%s' % (node_type, key))
                p, o = term, value

            if term is not None:
                prefix, _ = slurp.rdf_creators.find_rdf_prefix(term, prefixes)
                if prefix is not None:
                    prefixes_used.add(prefix)

                pos.append((p, o))

for prefix_used in prefixes_used:
    print('@prefix %s: <%s/> .' % (prefix_used, prefixes[prefix_used]))

print()

for s, po in subjects.items():
    n = 0
    limit = len(po)

    print('<%s>' % s)

    for p, o in po:
        n += 1
        p = slurp.rdf_creators.get_rdf_for_triple_part(p, prefixes)
        o = slurp.rdf_creators.get_rdf_for_triple_part(o, prefixes)

        print('  %s %s ' % (p, o), end='')

        if n < limit:
            print(';')
        else:
            print('.')
