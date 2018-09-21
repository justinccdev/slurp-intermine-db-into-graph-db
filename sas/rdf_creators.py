def create_node_subject(_id):
    """
    Create the RDF subject.  Currently hard-coded to gene with the ecogene prefix

    :param _id:
    :return:
    """
    return 'http://synbiomine.org/ecogene:%s' % _id


def find_rdf_prefix(term, extensions):
    """
    If the term has a known rdf prefix then return it

    :param term:
    :param extensions: dictionary of extensions to prefixes
    :return: (relevant_prefix|None, short_part_of_term)
    """
    extension, _, term = term.rpartition('/')
    return extensions.get(extension), term


def get_rdf_for_triple_part(part, prefixes):
    """
    Get the RDF for a raw triple part.  Either we need to substitute a prefix, put it in <> or leave it alone
    :param part:
    :param prefixes:
    :return:
    """
    prefix, short_term = find_rdf_prefix(part, prefixes)

    if prefix is not None:
        part = '%s:%s' % (prefix, short_term)
    elif part.startswith('http://'):
        part = '<%s>' % part
    elif part != 'a':
        part = '"%s"' % part

    return part