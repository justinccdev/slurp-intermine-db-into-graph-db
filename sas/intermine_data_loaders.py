def get_im_genes(curs, limit=None):
    _map = {
        # This is a hack because the primary identifier is not an accession number and the actual ncbigene ID is
        # not captured by Synbiomine
        'secondaryidentifier': 'id',
        'organismid': 'internal_organism_id',
        'sequenceontologytermid': 'internal_soterm_id',
        'primaryidentifier': 'name'
    }

    return map_rows_to_dicts(curs, 'gene', _map, limit)


def get_im_organisms(curs):
    _map = {
        'taxonid': 'id',
        'class': 'type',
    }

    return map_rows_to_dicts(curs, 'organism', _map)


def get_soterms(curs):
    _map = {
        'identifier': 'id',
        'ontologyid': 'internal_ontology_id'
    }

    return map_rows_to_dicts(curs, 'soterm', _map)


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
        print(row)

        for k, v in row.items():
            if k in _map:
                k = _map[k]

            if k is not None:
                entity[k] = v

        entities[row['id']] = entity

    return entities
