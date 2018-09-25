def add_entities(session, _type, entities):
    """
    Add entities
    :param session:
    :param _type:
    :param entities:
    :return:
    """

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


def add_relationships(curs, session):
    """
    Add relationships between entities
    :param conn:
    :param session:
    :return:
    """
    session.run("MATCH (g:gene), (o:organism) WHERE g.internal_organism_id = o.im_id CREATE (g)-[:organism]->(o)")
    session.run(
        "MATCH (g:gene), (s:soterm) WHERE g.internal_soterm_id = s.im_id CREATE (g)-[:sequenceOntologyTerm]->(s)")

    curs.execute("SELECT * from genesproteins")
    for row in curs:
        session.run(
            "MATCH (g:gene), (p:protein) WHERE g.im_id = %d AND p.im_id = %d CREATE (g)-[:protein]->(o)"
            % (row['genes'], row['proteins']))
