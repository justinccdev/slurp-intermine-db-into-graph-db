def create_node_subject(_id):
    """
    Create the RDF subject.  Currently hard-coded to gene with the ecogene prefix

    :param _id:
    :return:
    """

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


def get_term_for_class(class_type, terms_for_classes):
    """
    Get the ontology term for a class if it's available.

    :param class_type:
    :param terms_for_classes:
    :return: The term string or None if no term
    """
    if class_type in terms_for_classes:
        return terms_for_classes[class_type]
    else:
        return None


def process_class_type(class_type, terms_for_classes, prefixes, prefixes_used, subjects, gene_id):
    """
    Process the graph node type into something we can use to generate RDF.

    :param class_type:
    :param terms_for_classes:
    :param prefixes:
    :param prefixes_used:
    :param subjects:
    :param gene_id:
    :return:
    """
    term = get_term_for_class(class_type, terms_for_classes)

    prefix, _ = find_rdf_prefix_if_available(term, prefixes)
    if prefix is not None:
        prefixes_used.add(prefix)

    subjects[create_node_subject(gene_id)] = ('a', term)
