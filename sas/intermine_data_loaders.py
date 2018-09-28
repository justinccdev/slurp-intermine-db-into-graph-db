def get_collection_table_name(node):
    return '%s%s' % (node['reverse-reference'], node['name'])


def get_referenced_im_ids(curs, source_type, source_im_ids, referenced_type, intermine_model):
    """
    Find all the intermine IDs referenced by a given set of intermine IDs

    :param curs:
    :param source_type:
    :param source_im_ids:
    :param referenced_type:
    :param intermine_model:
    :return:
    """
    referenced_im_ids = []

    paths = list(filter(lambda k: k.startswith('%s.' % source_type), intermine_model.keys()))
    referenced_type_paths \
        = list(filter(lambda k: intermine_model[k].get('referenced-type') == referenced_type, paths))

    for im_id in source_im_ids:
        nodes = [intermine_model[path] for path in referenced_type_paths]
        for node in nodes:
            if node['flavour'] == 'reference':
                table_name = source_type.lower()
                column_name = '%sid' % node['name'].lower()
                curs.execute('SELECT %s FROM %s WHERE id=%s' % (column_name, table_name, im_id))
                referenced_im_ids.append(str(curs.fetchone()[column_name]))

            elif node['flavour'] == 'collection':
                table_name = get_collection_table_name(node)
                curs.execute(
                    'SELECT %s FROM %s WHERE %s=%s' % (node['name'], table_name, node['reverse-reference'], im_id))

                for row in curs:
                    referenced_im_ids.append(str(row[node['name']]))

    return referenced_im_ids


def map_rows_to_dicts(curs, intermine_class, _map, intermine_model, restriction_list=None):
    """
    Map rows from the InterMine database into dictionaries that will then be added to Neo4J

    :param curs: Postgres cursor
    :param intermine_class:
    :param _map: Map of InterMine class property names to Neo4J property names, where this translation is necessary.
    :param intermine_model
    :param restriction_list: List of intermine IDs to push into Neo4J. If None then all IDs for that class are pushed.
    :return:
    """
    entities = {}

    cmd = 'SELECT * FROM %s' % intermine_class

    if restriction_list is not None:
        if not restriction_list:
            return {}

        print(','.join(restriction_list))
        cmd += ' WHERE id IN (%s)' % ','.join(restriction_list)

    print(cmd)
    curs.execute(cmd)

    attrs = [p.partition('.')[2] for p in intermine_model if p.startswith('%s.' % intermine_class)]

    for row in curs:
        entity = {}

        for attr in sorted(attrs):
            # We need to do this kind of jiggery-pokerey because InterMine only uses lowercase postgres columns
            node_flavour = intermine_model['%s.%s' % (intermine_class, attr)]['flavour']

            if node_flavour == 'attribute':
                lc_attr = attr.lower()
            else:
                lc_attr = attr = '%sid' % attr.lower()

            print('Looking for [%s, %s]' % (lc_attr, attr))

            if lc_attr in row:
                if attr in _map:
                    attr = _map[attr]
                    print('Transformed to %s' % attr)

                if attr is not None:
                    entity[attr] = row[lc_attr]

        # FIXME: Yes, in my hacking about I've ended up hard-coding things that need to be removed again
        entity['im_id'] = row['id']
        entity['type'] = row['class']

        entities[row['id']] = entity

        print(entity)

    return entities
