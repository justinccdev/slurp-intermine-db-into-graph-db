def add_genes(session, genes):
    for im_id, gene in genes.items():
        print(gene)

        command = 'CREATE (:gene {'

        count = 0
        limit = len(gene)
        for k, v in gene.items():
            count += 1
            command += " %s:'%s'" % (k, v)

            if count < limit:
                command += ','

        command += ' })'

        session.run(command)


def add_organisms(session, organisms):
    for im_id, organism in organisms.items():
        print(organism)
        session.run(
            "CREATE (:organism { im_id:'%s', id:'%s', name: '%s', type:'%s' })"
            % (im_id, organism['external_primary_id'], organism['name'], organism['type']))


def add_relationships(session, genes):
    for im_id, gene in genes.items():
        session.run(
            "MATCH (g:gene {im_id:'%s'}), (o:organism {im_id:'%s'}) CREATE (g)-[:IN_GENOME_OF]->(o)"
            % (im_id, gene['internal_organism_id']))
