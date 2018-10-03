from lxml import etree


class InterMineModel:
    def __init__(self, model_path):
        self._model = self._load_model(model_path)

    def __getitem__(self, path):
        return self._model[path]

    def __contains__(self, path):
        return path in self._model

    def get(self, path):
        return self._model.get(path)

    def keys(self):
        return self._model.keys()

    def get_classes(self):
        return sorted(set([p.partition('.')[0] for p in self._model.keys()]))

    def get_paths_for_class(self, _class):
        return sorted(list(filter(lambda k: k.startswith('%s.' % _class), self.keys())))

    def get_paths_for_class_referencing_type(self, _class, referenced_type):
        return sorted(list(
            filter(
                lambda k: self._model[k].get('referenced-type') == referenced_type, self.get_paths_for_class(_class))))

    def get_attributes_for_class(self, _class):
        return sorted(list([p.partition('.')[2] for p in self._model if p.startswith('%s.' % _class)]))

    @staticmethod
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

    def _load_model(self, model_path):
        """
        Load an InterMine model

        :param model_path:
        :return:
        """
        xml_tree = etree.parse(model_path)

        model_nodes = {}

        # Record terms for classes and properties
        for _class in xml_tree.xpath('//class'):
            attrib = _class.attrib
            class_name = attrib['name']

            model_nodes[class_name] = {'flavour': 'class', 'class':class_name}
            if 'term' in attrib:
                model_nodes[class_name]['term'] = attrib['term']

            for _property in xml_tree.xpath("//class[@name='%s']/*" % class_name):
                attrib = _property.attrib

                model_path = '%s.%s' % (class_name, attrib['name'])
                model_nodes[model_path] = {'flavour': _property.tag, 'class':class_name}

                # Get all the other XML attribs in case we need them later.
                # It will be impossible for any to have the same name as the model_path
                # since XML attribs can't contain periods.
                model_nodes[model_path].update(attrib)

        # Now go through the class tree and copy ancestor class properties into descendants
        class_tree = self._build_class_tree_from_xml_tree(xml_tree)

        def get_ancestor_paths(_class):
            paths = []

            # We need to ignore any ancestor that isn't actually present in the model.
            # At least some InterMine models are guilty of this by specifying 'java.lang.Object'
            if _class not in class_tree:
                return paths

            parents = class_tree[_class]

            if parents:
                for parent in parents:
                    paths.extend(get_ancestor_paths(parent))

            for node in model_nodes:
                if node.startswith('%s.' % _class) and node != _class:
                    paths.append(node)

            return paths

        for _class in xml_tree.xpath('//class'):
            attrib = _class.attrib
            class_name = attrib['name']

            for path in get_ancestor_paths(class_name):
                node = model_nodes[path]
                simple_path_name = path.rpartition('.')[2]
                model_path = '%s.%s' % (class_name, simple_path_name)
                model_nodes[model_path] = node

        """
        for k, v in sorted(model_nodes.items()):
            print('Model term (%s,%s)' % (k, v))
        """

        return model_nodes
