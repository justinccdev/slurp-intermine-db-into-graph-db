def get_im_genes(curs):
    curs.execute("SELECT * FROM gene LIMIT 5")

    _map = {
        # This is a hack because the primary identifier is not an accession number and the actual ncbigene ID is
        # not captured by Synbiomine
        'secondaryidentifier':'id',
        'organismid':'internal_organism_id',
        'primaryidentifier':'name',
        'class':'type',
        'id':'im_id'
    }

    genes = {}

    for row in curs:
        gene = {}
        print(row)

        for k, v in row.items():
            if k in _map:
                k = _map[k]

            if k is not None:
                gene[k] = v

        genes[row['id']] = gene

    return genes


def get_im_organisms(curs):
    curs.execute("SELECT * FROM organism")

    organisms = {}

    for row in curs:
        organisms[row['id']] = {
            'id': row['taxonid'],
            'im_id': row['id'],
            'name': row['name'],
            'type': row['class']
        }

    return organisms
