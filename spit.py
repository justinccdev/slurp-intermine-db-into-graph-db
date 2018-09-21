#!/usr/bin/env python3

import argparse

import neo4j.v1

import sas.intermine_model_loaders
import sas.loaders
import sas.rdf_creators

parser = argparse.ArgumentParser('Spit out RDF for a given gene ID (try EG11277)')
parser.add_argument('id', help='Gene ID')
args = parser.parse_args()

fair_prefixes = sas.loaders.load_fair_prefixes('config/fair-prefixes.xml')
rdf_prefixes = sas.loaders.load_rdf_prefixes('config/rdf-prefixes.xml')
model_terms = sas.intermine_model_loaders.load_terms('intermine/genomic_model.xml')

prefixes_used = set()
subjects = {}

with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
    with driver.session() as session:
        result = session.run("match (n {id:'%s'}) return n" % args.id)
        record = result.single()
        node = record['n']

        subject_name = sas.rdf_creators.create_node_subject(node, fair_prefixes)
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
                prefix, _ = sas.rdf_creators.find_rdf_prefix(term, rdf_prefixes)
                if prefix is not None:
                    prefixes_used.add(prefix)

                pos.append((p, o))

print(sas.rdf_creators.create_rdf_output(rdf_prefixes, prefixes_used, subjects), end='')
