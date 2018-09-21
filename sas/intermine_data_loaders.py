def get_im_genes(curs):
    curs.execute("SELECT * FROM gene LIMIT 5")

    _genes = {}

    for row in curs:
        _genes[row['id']] = {
            # This is a hack because the primary identifier is not an accession number and the actual ncbigene ID is
            # not captured by Synbiomine
            'external_primary_id': row['secondaryidentifier'],
            'internal_organism_id': row['organismid'],
            'name': row['primaryidentifier'],
            'symbol' : row['symbol'],
            'type': row['class']
        }

    return _genes


def get_im_organisms(_curs):
    _curs.execute("SELECT * FROM organism")

    organisms = {}

    for row in _curs:
        organisms[row['id']] = {
            'external_primary_id': row['taxonid'],
            'name': row['name'],
            'type': row['class']
        }

    return organisms
