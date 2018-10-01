def get_collection_table_name(node, intermine_model):
    """
    Get the table name for this collection

    :param node:
    :param intermine_model:
    :return: (table-name, reference-column-name).  table-name will be null if there isn't a collection table for this node
    """

    if 'reverse-reference' in node:
        referenced_path = '%s.%s' % (node['referenced-type'], node['reverse-reference'])
        referenced_node = intermine_model.get(referenced_path)

        # If the referenced node is an attribute then there will be no table
        if referenced_node is not None and referenced_node['flavour'] != 'collection':
            return None, None

    part1 = node['name'].lower()

    if 'reverse-reference' in node:
        reverse_reference_name = node['reverse-reference'].lower()
    else:
        reverse_reference_name = node['referenced-type'].lower()

    part2 = reverse_reference_name

    # The first name in the alphabet is the first part of the table name
    if part1 > part2:
        part1, part2 = part2, part1

    return part1 + part2, reverse_reference_name


def get_referenced_im_ids(curs, source_class, source_im_ids, referenced_class, intermine_model):
    """
    Find all the intermine IDs referenced by a given set of intermine IDs

    :param curs:
    :param source_class:
    :param source_im_ids:
    :param referenced_class:
    :param intermine_model:
    :return:
    """
    # print('Looking for %s referencing %s' % (source_class, referenced_class))

    referenced_im_ids = set(source_im_ids)
    referenced_type_paths = intermine_model.get_paths_for_class_referencing_type(source_class, referenced_class)
    print(referenced_type_paths)

    for im_id in source_im_ids:
        nodes = [intermine_model[path] for path in referenced_type_paths]
        for node in nodes:
            print(node)
            if node['flavour'] == 'reference':
                table_name = source_class.lower()
                column_name = '%sid' % node['name'].lower()
                cmd = 'SELECT %s FROM %s WHERE id=%s' % (column_name, table_name, im_id)
                print(cmd)
                curs.execute(cmd)
                referenced_im_ids.add(str(curs.fetchone()[column_name]))

            elif node['flavour'] == 'collection':
                table_name, ref_col_name = get_collection_table_name(node, intermine_model)

                if table_name is not None:
                    cmd = 'SELECT %s FROM %s WHERE %s=%s' % (node['name'], table_name, ref_col_name, im_id)
                    print(cmd)
                    curs.execute(cmd)

                    for row in curs:
                        referenced_im_ids.add(str(row[node['name'].lower()]))

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

    attrs = intermine_model.get_attributes_for_class(intermine_class)

    for row in curs:
        entity = {}

        for attr in sorted(attrs):
            # We need to do this kind of jiggery-pokerey because InterMine only uses lowercase postgres columns
            node_flavour = intermine_model['%s.%s' % (intermine_class, attr)]['flavour']

            if node_flavour == 'attribute':
                lc_attr = attr.lower()
            else:
                lc_attr = attr = '%sid' % attr.lower()

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
