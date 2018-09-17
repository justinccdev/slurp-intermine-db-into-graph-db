def get_im_genes(_curs):
    _curs.execute("SELECT id, primaryidentifier, organismid, class FROM gene LIMIT 5")

    _genes = {}

    for row in _curs:
        _genes[row['id']] = {
            'external_primary_id': row['primaryidentifier'],
            'internal_organism_id': row['organismid'],
            'type': row['class']
        }

    return _genes


def get_im_organisms(_curs):
    _curs.execute("SELECT id, taxonid, name, class FROM organism")

    organisms = {}

    for row in _curs:
        organisms[row['id']] = {
            'external_primary_id': row['taxonid'],
            'name': row['name'],
            'type': row['class']
        }

    return organisms