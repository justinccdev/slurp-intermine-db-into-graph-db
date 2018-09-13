#!/usr/bin/env python3

import neo4j.v1
import psycopg2.extras


def get_im_genes(_curs):
    _curs.execute("SELECT id, primaryidentifier, organismid, class FROM gene LIMIT 5")

    _genes = {}

    for row in _curs:
        _genes[row['id']] = {
            'external_primary_id': row['primaryidentifier'],
            'internal_organism_id': row['organismid'],
            'type': row['class']
        }

    return _genes


def get_im_organisms(_curs):
    _curs.execute("SELECT id, taxonid, name, class FROM organism")

    organisms = {}

    for row in _curs:
        organisms[row['id']] = {'external_primary_id': row['taxonid'], 'name': row['name'], 'type': row['class']}

    return organisms


def add_genes(_genes):
    for im_id, gene in _genes.items():
        print(gene)
        session.run(
            "CREATE (:gene { im_id:'%s', id:'%s', type:'%s' })" % (im_id, gene['external_primary_id'], gene['type']))


def add_organisms(_organisms):
    for im_id, organism in _organisms.items():
        print(organism)
        session.run(
            "CREATE (:organism { im_id:'%s', id:'%s', name: '%s', type:'%s' })"
            % (im_id, organism['external_primary_id'], organism['name'], organism['type']))


def add_relationships(_genes):
    for im_id, gene in _genes.items():
        session.run(
            "MATCH (g:gene {im_id:'%s'}), (o:organism {im_id:'%s'}) CREATE (g)-[:IN_GENOME_OF]->(o)"
            % (im_id, gene['internal_organism_id']))


conn = psycopg2.connect(dbname='synbiomine-v6', user='justincc', cursor_factory=psycopg2.extras.DictCursor)

with neo4j.v1.GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'passw0rd')) as driver:
    with driver.session() as session:
        with conn.cursor() as curs:
            genes = get_im_genes(curs)
            add_genes(genes)
            add_organisms(get_im_organisms(curs))
            add_relationships(genes)

conn.close()
