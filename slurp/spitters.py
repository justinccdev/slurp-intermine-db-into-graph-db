from lxml import etree


def get_terms_for_classes(model_path):
    tree = etree.parse(model_path)
    model_package = tree.xpath('//model/@package')

    terms_for_classes = {}

    for _class in tree.xpath('//class'):
        attrib = _class.attrib

        if 'term' in attrib:
            terms_for_classes[model_package[0] + '.' + attrib['name']] = attrib['term']

    """
    for k, v in terms_for_classes.items():
        print(k, v)
    """

    return terms_for_classes
