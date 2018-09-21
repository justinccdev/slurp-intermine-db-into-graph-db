def create_node_subject(node, fair_prefixes):
    """
    Create the RDF subject.  Currently hard-coded to gene with the ecogene prefix

    :param node
    :param fair_prefixes
    :return:
    """
    prefix = fair_prefixes.get(node['type'], 'unknown')

    return 'http://synbiomine.org/%s:%s' % (prefix, node['id'])


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


def create_rdf_output(prefixes, prefixes_used, subjects):
    """
    Create the final rdf output
    :param prefixes:
    :param prefixes_used:
    :param subjects:
    :return:
    """
    output = ''

    for prefix_used in sorted(prefixes_used):
        output += '@prefix %s: <%s/> .\n' % (prefix_used, prefixes[prefix_used])

    output += '\n'

    for s, po in subjects.items():
        n = 0
        limit = len(po)

        output += '<%s>\n' % s

        for p, o in po:
            n += 1
            p = get_rdf_for_triple_part(p, prefixes)
            o = get_rdf_for_triple_part(o, prefixes)

            output += '  %s %s ' % (p, o)

            if n < limit:
                output += ';'
            else:
                output += '.'

            output += '\n'

    return output
