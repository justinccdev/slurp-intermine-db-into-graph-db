def map_rows_to_dicts(curs, _type, _map, restriction_list=None):
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
