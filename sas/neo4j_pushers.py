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


def add_relationships(curs, session, restrictions):
    """
    Add relationships between entities
    :param conn:
    :param session:
    :return:
    """

    print('Adding Gene->Organism relationships')
    session.run("MATCH (g:Gene),(o:Organism) WHERE g.internal_organism_id = o.im_id CREATE (g)-[:organism]->(o)")

    print('Adding Gene->SOTerm relationsihps')
    session.run(
        "MATCH (g:Gene),(s:SOTerm) WHERE g.internal_soterm_id = s.im_id CREATE (g)-[:sequenceOntologyTerm]->(s)")

    print('Adding Gene->Protein relationships')

    cmd = 'SELECT * from genesproteins'

    if restrictions is not None:
        if not restrictions:
            return {}

        print(','.join(restrictions))
        cmd += ' WHERE genes IN (%s)' % ','.join(restrictions)

    curs.execute(cmd)

    i = 0
    for row in curs:
        i += 1
        print('Assessing genesproteins row %d' % i)

        cmd = "MATCH (g:Gene),(p:Protein) WHERE g.im_id = '%d' AND p.im_id = '%d' CREATE (g)-[:proteins]->(p)" \
            % (row['genes'], row['proteins'])

        print(cmd)

        session.run(cmd)
