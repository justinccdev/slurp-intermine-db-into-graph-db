def get_im_genes(curs):
    curs.execute("SELECT * FROM gene LIMIT 5")

    _map = {
        # This is a hack because the primary identifier is not an accession number and the actual ncbigene ID is
        # not captured by Synbiomine
        'secondaryidentifier':'external_primary_id',
        'organismid':'internal_organism_id',
        'primaryidentifier':'name',
        'class':'type',
        'id':None
    }

    _genes = {}

    for row in curs:
        gene = {}

        for k, v in row.iteritems():
            if k in map:
                k = _map[k]

            if k is not None:
                gene[k] = v

        _genes[row['id']] = gene

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
