def create_node_fair_uri(node, fair_prefixes):
    """
    Create the RDF subject.  Currently hard-coded to gene with the ecogene prefix

    :param node
    :param fair_prefixes
    :return:
    """
    prefix = fair_prefixes.get(node['class'], 'unknown')
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


def process_node_properties(node, node_type, intermine_model, rdf_prefixes, prefixes_used, pos):
    """
    Process the properties of a graph node
    :param node:
    :param node_type:
    :param intermine_model:
    :param rdf_prefixes:
    :param prefixes_used:
    :param pos:
    :return:
    """
    for key, value in sorted(node.items()):
        print('KEY-VALUE: %s,%s' % (key, value))

        if key == 'class':
            term = intermine_model.get(node_type).get('term')
            p, o = 'a', term
        else:
            path = '%s.%s' % (node_type, key)
            print('Looking for path [%s]' % path)

            node = intermine_model.get(path)
            term = node.get('term') if node else None

            p, o = term, value

        print('Term was [%s]' % term)
        if term:
            prefix, _ = find_rdf_prefix(term, rdf_prefixes)
            if prefix:
                prefixes_used.add(prefix)

            pos.append((p, o))


def process_node_relationships(
        relationships, intermine_class, intermine_model, rdf_prefixes, prefixes_used, fair_prefixes, pos):
    """
    Process the relationships of a graph node
    :param relationships:
    :param intermine_class:
    :param intermine_model:
    :param rdf_prefixes:
    :param prefixes_used:
    :param fair_prefixes:
    :param pos:
    :return:
    """
    for record in relationships:
        predicate = record['type(r)']
        print(predicate)
        node = intermine_model.get('%s.%s' % (intermine_class, predicate))

        if not node:
            continue

        term = node.get('term')

        if term:
            prefix, _ = find_rdf_prefix(term, rdf_prefixes)
            if prefix:
                prefixes_used.add(prefix)

            object_name = create_node_fair_uri(record['b'], fair_prefixes)
            pos.append((term, object_name))


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
            output += ';' if n < limit else '.'
            output += '\n'

    return output
