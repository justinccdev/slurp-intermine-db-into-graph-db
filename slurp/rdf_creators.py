def create_node_subject(_id):
    return 'http://synbiomine.org/ncbi:%s' % _id


def find_rdf_prefix_if_available(term, prefixes):
    resource = term.rpartition('/')[0]
    if resource in prefixes:
        return resource
