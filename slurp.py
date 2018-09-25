#!/usr/bin/env python3

import argparse

import neo4j.v1
import psycopg2.extras

import sas.neo4j_pushers
import sas.intermine_data_loaders


# Map intermine columns to neo4j properties.
# Implicitly, we are doing
# { 'id': 'im_id',
#   'class': 'type }
# for everything
intermine_to_neo4j_map = {
    'gene': {
        # This is a hack because the primary identifier is not an accession number and the actual ncbigene ID is
        # not captured by Synbiomine
        'secondaryidentifier': 'id',
        'organismid': 'internal_organism_id',
        'sequenceontologytermid': 'internal_soterm_id',
        'primaryidentifier': 'name'
    },

    'organism': {
        'taxonid': 'id',
        'class': 'type'
    },

    'protein': {
        'primaryaccession': 'id'
    },

    'soterm': {
        'identifier': 'id',
        'ontologyid': 'internal_ontology_id'
    }
}

parser = argparse.ArgumentParser('Slurp InterMine data into Neo4J')
parser.add_argument('--limit', type=int, help='limit number of genes slurped for quicker testing')
args = parser.parse_args()


with psycopg2.connect(dbname='synbiomine-v5-poc4', user='justincc', cursor_factory=psycopg2.extras.DictCursor) as conn:
    with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
        with driver.session() as session:
            with conn.cursor() as curs:
                for intermine_class, _map in intermine_to_neo4j_map.items():
                     sas.neo4j_pushers.add_entities(
                         session,
                         intermine_class,
                         sas.intermine_data_loaders.map_rows_to_dicts(curs, intermine_class, _map, args.limit))

                sas.neo4j_pushers.add_relationships(curs, session)
