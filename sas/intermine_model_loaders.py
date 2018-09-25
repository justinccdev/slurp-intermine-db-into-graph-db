from lxml import etree


def build_class_tree_from_xml_tree(xml_tree):
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


def load_terms(model_path):
    """
    Load available terms from the InterMine model

    :param model_path:
    :return:
    """
    xml_tree = etree.parse(model_path)
    # model_package = xml_tree.xpath('//model/@package')[0]

    model_terms = {}

    # Record terms for classes and properties
    for _class in xml_tree.xpath('//class'):
        attrib = _class.attrib
        class_name = attrib['name']

        if 'term' in attrib:
            # model_terms[model_class] = attrib['term']
            model_terms[class_name] = attrib['term']

        for _property in xml_tree.xpath("//class[@name='%s']/*" % class_name):
            attrib = _property.attrib

            if 'term' in attrib:
                model_node = '%s.%s' % (class_name, attrib['name'])
                model_terms[model_node] = attrib['term']

    # Now go through the class tree and copy ancestor class properties into descendants
    class_tree = build_class_tree_from_xml_tree(xml_tree)

    def get_ancestor_attributes(_class):
        attributes = []

        # We need to ignore any ancestor that isn't actually present in the model.  At least some InterMine models are
        # guilty of this by specifying 'java.lang.Object'
        if _class not in class_tree:
            return attributes

        parents = class_tree[_class]

        if parents is not None:
            for parent in parents:
                attributes.extend(get_ancestor_attributes(parent))

        for _term in model_terms:
            if _term.startswith(_class) and _term != _class:
                attributes.append(_term)

        return attributes

    for _class in xml_tree.xpath('//class'):
        attrib = _class.attrib
        class_name = attrib['name']

        for ancestor_attribute in get_ancestor_attributes(class_name):
            term = model_terms[ancestor_attribute]
            simple_attribute_name = ancestor_attribute.rpartition('.')[2]
            model_node = '%s.%s' % (class_name, simple_attribute_name)
            model_terms[model_node] = term

    """
    for k, v in model_terms.items():
        print('Model term (%s,%s)' % (k, v))
    """

    return model_terms
