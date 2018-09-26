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


def add_relationships(curs, session, source_class, target_classes, intermine_model, restrictions):
    """
    Add relationships between entities
    :param conn:
    :param session:
    :param source_class: The source class to add relationships
    :param target_classes: The target classes for adding relationships
    :param intermine_model:
    :param restrictions:
    :return:
    """

    for target_class in target_classes:
        print('Adding %s->%s relationships' % (source_class, target_class))

        paths = filter(lambda k: k.startswith('%s.' % source_class), intermine_model.keys())
        for path in paths:
            node = intermine_model[path]

            if node['type'] == 'reference':
                column_name = '%sid' % node['name'].lower()

                cmd = "MATCH (s:%s),(t:%s) WHERE s.%s = t.im_id CREATE (s)-[:%s]->(t)" \
                      % (source_class, target_class, column_name, node['name'])

                print(cmd)
                session.run(cmd)

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
