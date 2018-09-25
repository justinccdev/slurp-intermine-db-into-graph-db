def add_entities(session, _type, entities):
    """
    Add entities
    :param session:
    :param _type:
    :param entities:
    :return:
    """

    # Need to create an index for more efficient joining when we need to connect intermine neo4j entities by their
    # im_id
    session.run('CREATE INDEX ON :%s(im_id)' %_type)

    i = 0

    for im_id, entity in entities.items():
        i += 1

        print('Processing %d of %d %s' % (i, len(entities), _type))

        # print(entity)

        cmd = 'CREATE (:%s {' % _type

        count = 0
        limit = len(entity)
        for k, v in entity.items():
            count += 1

            # Escape single quotes
            if v is not None and isinstance(v, str):
                v = v.replace("'", "\\'")

            cmd += " %s:'%s'" % (k, v)

            if count < limit:
                cmd += ','

        cmd += ' })'

        # print('Command [%s]' % cmd)

        session.run(cmd)


def add_relationships(curs, session, restriction_list):
    """
    Add relationships between entities
    :param conn:
    :param session:
    :return:
    """

    print('Adding gene->organism relationships')
    session.run("MATCH (g:gene),(o:organism) WHERE g.internal_organism_id = o.im_id CREATE (g)-[:organism]->(o)")

    print('Adding gene->soterm relationsihps')
    session.run(
        "MATCH (g:gene),(s:soterm) WHERE g.internal_soterm_id = s.im_id CREATE (g)-[:sequenceOntologyTerm]->(s)")

    print('Adding gene->protein relationships')

    cmd = 'SELECT * from genesproteins'

    if restriction_list is not None:
        if not restriction_list:
            return {}

        print(','.join(restriction_list))
        cmd += ' WHERE genes IN (%s)' % ','.join(restriction_list)

    curs.execute(cmd)

    i = 0
    for row in curs:
        i += 1
        print('Assessing genesproteins row %d' % i)

        cmd = "MATCH (g:gene),(p:protein) WHERE g.im_id = '%d' AND p.im_id = '%d' CREATE (g)-[:proteins]->(p)" \
            % (row['genes'], row['proteins'])

        print(cmd)

        session.run(cmd)
