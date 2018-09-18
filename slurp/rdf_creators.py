def create_node_subject(_id):
    return 'http://synbiomine.org/ecogene:%s' % _id


def find_rdf_prefix_if_available(term, extensions):
    """
    If the term has a known rdf prefix then return it

    :param term:
    :param extensions: dictionary of extensions to prefixes
    :return: (relevant_prefix|None, short_part_of_term)
    """

    extension, _, term = term.rpartition('/')
    if extension in extensions:
        return extensions[extension], term
    else:
        return None, term
