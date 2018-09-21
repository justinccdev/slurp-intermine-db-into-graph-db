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


def process_class_type(class_type, model_terms, prefixes, prefixes_used, subject):
    """
    Process the graph node type into something we can use to generate RDF.

    :param class_type:
    :param model_terms:
    :param prefixes:
    :param prefixes_used:
    :param subjects:
    :return:
    """
    term = model_terms.get(class_type.rpartition('.')[2])
     # print('Got term %s' % term)

    if term is not None:
        prefix, _ = find_rdf_prefix(term, prefixes)
        if prefix is not None:
            prefixes_used.add(prefix)

        subject.append(('a', term))


def process_symbol(model_node, symbol, model_terms, prefixes, prefixes_used, subject):
    """
    Process a symbol graph node property into something we can use to generate RDF.

    :param symbol:
    :param terms_for_classes:
    :param prefixes:
    :param prefixes_used:
    :param subjects:
    :param gene_id:
    :return:
    """
    # print('MODEL NODE %s' % model_node)
    term = model_terms.get(model_node)

    # print('term for %s is %s' % (model_node, term))

    if term is not None:
        prefix, _ = find_rdf_prefix(term, prefixes)
        if prefix is not None:
            prefixes_used.add(prefix)

        subject.append((term, symbol))
