import sas.intermine_data_loaders


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
    session.run('CREATE INDEX ON :%s(im_id)' % _type)

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
    :param curs:
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
        for path in sorted(paths):
            print('Processing path %s' % path)

            node = intermine_model[path]
            if node.get('referenced-type') != target_class:
                continue

            if node['type'] == 'reference':
                column_name = '%sid' % node['name'].lower()

                cmd = "MATCH (s:%s),(t:%s) WHERE s.%s = t.im_id CREATE (s)-[:%s]->(t)" \
                      % (source_class, target_class, column_name, node['name'])

                # print(cmd)
                session.run(cmd)

            elif node['type'] == 'collection':
                if 'reverse-reference' not in node:
                    print('No reverse-reference for %s to build table name. Skipping' % path)
                    continue

                table_name = sas.intermine_data_loaders.get_collection_table_name(node)

                curs.execute("SELECT to_regclass('%s')" % table_name)
                if not curs.fetchone()[0]:
                    print('Table %s for adding relationships does not exist. Skipping' % table_name)
                    continue

                cmd = 'SELECT * from %s' % table_name

                if restrictions is not None:
                    if not restrictions:
                        continue

                    # print(','.join(restrictions))
                    cmd += ' WHERE %s IN (%s)' % (node['reverse-reference'], ','.join(restrictions))

                # print(cmd)
                curs.execute(cmd)

                i = 0
                for row in curs:
                    i += 1
                    # print('Assessing %s row %d' % (table_name, i))

                    cmd = "MATCH (s:%s),(t:%s) WHERE s.im_id = '%d' AND t.im_id = '%d' CREATE (s)-[:%s]->(t)" \
                        % (source_class, target_class,
                           row[node['reverse-reference'].lower()], row[node['name'].lower()], node['name'])

                    """
                    if path == 'Gene.proteins':
                        print(cmd)
                    """

                    session.run(cmd)
