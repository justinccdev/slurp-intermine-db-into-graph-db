#!/usr/bin/env python3

import argparse

import neo4j.v1

import sas.intermine_model_loaders
import sas.config_loaders
import sas.rdf_creators

parser = argparse.ArgumentParser('Spit out RDF for a given gene ID (try EG11277)')
parser.add_argument('id', help='Gene ID')
args = parser.parse_args()

fair_prefixes = sas.config_loaders.load_fair_prefixes('config/fair-prefixes.xml')
rdf_prefixes = sas.config_loaders.load_rdf_prefixes('config/rdf-prefixes.xml')
model_terms = sas.intermine_model_loaders.load_model('intermine/genomic_model.xml')

prefixes_used = set()
subjects = {}

with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
    with driver.session() as session:
        result = session.run("MATCH (n {id:'%s'}) RETURN n" % args.id)
        record = result.single()
        node = record['n']

        subject_name = sas.rdf_creators.create_node_fair_uri(node, fair_prefixes)
        pos = []
        subjects[subject_name] = pos

        node_type = node['type'].rpartition('.')[2]

        sas.rdf_creators.process_node_properties(node, node_type, model_terms, rdf_prefixes, prefixes_used, pos)

        # look for relationships
        result = session.run("MATCH (g:Gene {id:'%s'})-[r]-(b) RETURN type(r), b" % args.id)

        sas.rdf_creators.process_node_relationships(
            result, node_type, model_terms, rdf_prefixes, prefixes_used, fair_prefixes, pos)

print(sas.rdf_creators.create_rdf_output(rdf_prefixes, prefixes_used, subjects), end='')
