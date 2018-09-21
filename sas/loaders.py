from lxml import etree


def load_fair_prefixes(prefixes_path):
    prefixes = {}

    tree = etree.parse(prefixes_path)
    for prefix in tree.xpath('//prefix'):
        prefixes[prefix.attrib['class']] = prefix.attrib['prefix']

    return prefixes


def load_rdf_prefixes(prefixes_path):
    """
    Load extensions to rdf prefixes and return a dictionary with entries in both directions.
    We can do this since extensions always start with http:// but prefixes never will

    :param prefixes_path:
    :return:
    """

    prefixes = {}

    tree = etree.parse(prefixes_path)
    for prefix in tree.xpath('//prefix'):
        prefixes[prefix.attrib['extension']] = prefix.attrib['prefix']
        prefixes[prefix.attrib['prefix']] = prefix.attrib['extension']

    return prefixes
