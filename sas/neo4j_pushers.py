import sas.intermine_data_loaders


def add_entities(session, intermine_class, entities):
    """
    Add entities
    :param session:
    :param intermine_class:
    :param entities:
    :return:
    """

    # Need to create an index for more efficient joining when we need to connect intermine neo4j entities by their
    # im_id
    session.run('CREATE INDEX ON :%s(im_id)' % intermine_class)

    i = 0
    entities_count = len(entities)

    for im_id, entity in entities.items():
        i += 1

        # XXX: A failed attempt to adjust the referenced class for child referenced classes (e.g. GOAnnotation
        # referencing OntologyTerm when actually this should be GOTerm. This might even be a bug in the construction
        # of the synbiomine-v5-poc4 database
        """
        cmd = 'SELECT class FROM intermineobject WHERE id=%d' % im_id
        curs.execute(cmd)
        new_class = curs.fetchone()['class'].rpartition('.')[2]
        if intermine_class == 'OntologyTerm': print(cmd)
        """

        print('Adding %d of %d %s' % (i, entities_count, intermine_class))

        # MERGE appears to the same as checking existence manually
        """
        cmd = "MATCH (n:%s) where n.im_id = '%d' return count(*)" % (intermine_class, im_id)
        result = session.run(cmd)
        record = result.single()
        if record['count(*)'] > 0:
            continue
            """

        cmd = 'MERGE (:%s {' % intermine_class

        count = 0
        limit = len(entity)
        for k, v in entity.items():
            count += 1

            # Escape single quotes
            if v and isinstance(v, str):
                v = v.replace("'", "\\'")

            cmd += " %s:'%s'" % (k, v)

            if count < limit:
                cmd += ','

        cmd += ' })'

        # print('Command [%s]' % cmd)

        session.run(cmd)


def add_relationships(curs, session, source_class, target_classes, intermine_model, selections):
    """
    Add relationships between entities
    :param curs:
    :param session:
    :param source_class: The source class to add relationships
    :param target_classes: The target classes for adding relationships
    :param intermine_model:
    :param selections:
    :return:
    """

    for target_class in target_classes:
        # print('Adding %s->%s relationships' % (source_class, target_class))

        paths = intermine_model.get_paths_for_class(source_class)
        for path in sorted(paths):

            node = intermine_model[path]

            # print('Processing node %s' % node)

            if node.get('referenced-type') != target_class:
                continue

            if node['flavour'] == 'reference':
                column_name = '%sid' % node['name'].lower()

                cmd = "MATCH (s:%s),(t:%s) WHERE s.%s = t.im_id MERGE (s)-[:%s]->(t)" \
                      % (source_class, target_class, column_name, node['name'])

                # if source_class == 'GOAnnotation' and target_class == 'OntologyTerm': print(cmd)
                session.run(cmd)

            elif node['flavour'] == 'collection':
                if 'reverse-reference' not in node:
                    print('No reverse-reference for %s to build table name. Skipping' % path)
                    continue

                table_name, _ = sas.intermine_data_loaders.get_collection_table_name(node, intermine_model)

                if not table_name:
                    continue

                curs.execute("SELECT to_regclass('%s')" % table_name)
                if not curs.fetchone()[0]:
                    print('Table %s for adding relationships does not exist. Skipping' % table_name)
                    continue

                cmd = "SELECT * FROM %s AS o, intermineobject AS i WHERE o.%s = i.id" \
                      " AND i.class = 'org.intermine.model.bio.%s'" \
                      % (table_name, node['reverse-reference'], source_class)

                if selections is not None:
                    if not selections:
                        continue

                    cmd += ' AND %s IN (%s)' % (node['reverse-reference'], ','.join(selections))
                    # print('Selecting: %s' % cmd)

                    # TODO: In a table like bioentitiespublications we could get a big efficiency gain if we
                    # also figured out all our selected bioentities and filtered on those too.

                curs.execute(cmd)

                i = 0
                for row in curs:
                    i += 1
                    # print('Assessing %s row %d' % (table_name, i))

                    cmd = "MATCH (s:%s),(t:%s) WHERE s.im_id = '%d' AND t.im_id = '%d' MERGE (s)-[:%s]->(t)" \
                        % (source_class, target_class,
                           row[node['reverse-reference'].lower()], row[node['name'].lower()], node['name'])

                    # print(cmd)
                    session.run(cmd)
