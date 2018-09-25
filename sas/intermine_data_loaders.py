def map_rows_to_dicts(curs, _type, _map, limit=None):
    _map['id'] = 'im_id'
    _map['class'] = 'type'

    entities = {}

    cmd = 'SELECT * FROM %s' % _type
    if limit is not None:
        cmd += ' LIMIT %d' % limit

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
