def get_im_ids_for_referenced_type(curs, source_type, source_im_ids, referenced_type, intermine_model):
    im_ids = []

    paths = list(filter(lambda k: k.startswith('%s.' % source_type), intermine_model.keys()))
    referenced_type_paths \
        = list(filter(lambda k: intermine_model[k].get('referenced-type') == referenced_type, paths))

    for im_id in source_im_ids:
        nodes = [intermine_model[path] for path in referenced_type_paths]
        for node in nodes:
            if node['type'] == 'collection':
                table_name = '%s%s' % (node['reverse-reference'], node['name'])
                curs.execute(
                    'SELECT %s FROM %s WHERE %s=%s' % (node['name'], table_name, node['reverse-reference'], im_id))

                for row in curs:
                    im_ids.append(str(row[node['name']]))

    return im_ids


def map_rows_to_dicts(curs, _type, _map, restriction_list=None):
    """
    Map rows from the InterMine database into dictionaries

    :param curs:
    :param _type:
    :param _map:
    :param restriction_list:
    :return:
    """
    entities = {}

    cmd = 'SELECT * FROM %s' % _type

    if restriction_list is not None:
        if not restriction_list:
            return {}

        print(','.join(restriction_list))
        cmd += ' WHERE id IN (%s)' % ','.join(restriction_list)

    print(cmd)
    curs.execute(cmd)

    for row in curs:
        entity = {}
        # print(row)

        for k, v in row.items():
            if k in _map:
                k = _map[k]

            if k is not None:
                entity[k] = v

        entities[row['id']] = entity

    return entities
