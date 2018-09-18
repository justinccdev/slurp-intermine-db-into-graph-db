from lxml import etree


def load_fair_prefixes(prefixes_path):
    prefixes = {}

    tree = etree.parse(prefixes_path)
    for prefix in tree.xpath('//prefix'):
        prefixes[prefix.attrib['class']] = prefix.attrib['prefix']

    return prefixes


def load_rdf_prefixes(prefixes_path):
    prefixes = {}

    tree = etree.parse(prefixes_path)
    for prefix in tree.xpath('//prefix'):
        prefixes[prefix.attrib['resource']] = prefix.attrib['prefix']

    return prefixes


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
