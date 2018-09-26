from lxml import etree


def _build_class_tree_from_xml_tree(xml_tree):
    """
    Given InterMine model XML, return a structure where children classes point to parents[]
    :param xml_tree:
    :return:
    """
    class_tree = {}

    for _class in xml_tree.xpath('//class'):
        attrib = _class.attrib

        if 'extends' in attrib:
            parents = attrib['extends'].split()
        else:
            parents = None

        class_tree[attrib['name']] = parents

    return class_tree


def load_model(model_path):
    """
    Load an InterMine model

    :param model_path:
    :return:
    """
    xml_tree = etree.parse(model_path)
    # model_package = xml_tree.xpath('//model/@package')[0]

    model_nodes = {}

    # Record terms for classes and properties
    for _class in xml_tree.xpath('//class'):
        attrib = _class.attrib
        class_name = attrib['name']

        model_nodes[class_name] = {'type': 'class'}
        if 'term' in attrib:
            # model_terms[model_class] = attrib['term']
            model_nodes[class_name]['term'] = attrib['term']

        for _property in xml_tree.xpath("//class[@name='%s']/*" % class_name):
            attrib = _property.attrib

            model_path = '%s.%s' % (class_name, attrib['name'])
            model_nodes[model_path] = {'type': _property.tag }

            # Get all the other XML attribs in case we need them later. It will be impossible for any to have the same
            # name as the model_path since XML attribs can't contain periods.
            model_nodes[model_path].update(attrib)

    # Now go through the class tree and copy ancestor class properties into descendants
    class_tree = _build_class_tree_from_xml_tree(xml_tree)

    def get_ancestor_paths(_class):
        paths = []

        # We need to ignore any ancestor that isn't actually present in the model.  At least some InterMine models are
        # guilty of this by specifying 'java.lang.Object'
        if _class not in class_tree:
            return paths

        parents = class_tree[_class]

        if parents is not None:
            for parent in parents:
                paths.extend(get_ancestor_paths(parent))

        for _term in model_nodes:
            if _term.startswith(_class) and _term != _class:
                paths.append(_term)

        return paths

    for _class in xml_tree.xpath('//class'):
        attrib = _class.attrib
        class_name = attrib['name']

        for path in get_ancestor_paths(class_name):
            node = model_nodes[path]
            simple_path_name = path.rpartition('.')[2]
            model_path = '%s.%s' % (class_name, simple_path_name)
            model_nodes[model_path] = node

    # print(model_nodes)

    for k, v in model_nodes.items():
        print('Model term (%s,%s)' % (k, v))


    return model_nodes
