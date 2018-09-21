def add_entities(session, _type, entities):
    """
    Add entities
    :param session:
    :param _type:
    :param entities:
    :return:
    """
    for im_id, entity in entities.items():
        print(entity)

        command = 'CREATE (:%s {' % _type

        count = 0
        limit = len(entity)
        for k, v in entity.items():
            count += 1
            command += " %s:'%s'" % (k, v)

            if count < limit:
                command += ','

        command += ' })'

        session.run(command)


def add_relationships(session, genes):
    """
    Add relationships between entities
    :param session:
    :param genes:
    :return:
    """
    for im_id, gene in genes.items():
        session.run(
            "MATCH (g:gene {im_id:'%s'}), (o:organism {im_id:'%s'}) CREATE (g)-[:organism]->(o)"
            % (im_id, gene['internal_organism_id']))
