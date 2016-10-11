class Skip(Exception): pass

def resolve(node, link_name, args={}):
    if link_name in node:
        link = node[link_name] 
    elif hasattr(node, link_name):
        link = getattr(node, link_name)
    else:
        assert False, (link_name, node)

    if callable(link):
        value = link(**args)
    else:
        value = link

    return value

class ScalarField:
    def __init__(self, name, alias=None, args={}, directives=()):
        self.name = name
        self.alias = alias
        self.args = args
        self.directives = directives

    def execute(self, root):
        return (self.alias or self.name, resolve(root, self.name, self.args))

    def __repr__(self):
        return self.name

class ObjectField:
    def __init__(self, name, fields, alias=None, args=(), directives=()):
        self.name = name
        self.fields = fields
        self.alias = alias
        self.args = args
        self.directives = directives

    def execute(self, root):
        if self.name:
            node = resolve(root, self.name, self.args)
        else:
            assert not self.args and not self.alias
            node = root

        if isinstance(node, list):
            result = [dict(field.execute(item) for field in self.fields) for item in node]
        else:
            result = dict(field.execute(node) for field in self.fields)
        return (self.alias or self.name, result)

    def __repr__(self):
        return '{} {{ {} }}'.format(self.name, ' '.join(str(field) for field in self.fields))

def dict_to_field(query_dict, name=None):
    def convert(key, value):
        if value is None:
            return ScalarField(key)
        else:
            return ObjectField(key, [convert(key, value) for key, value in value.items()])
    return convert(name, query_dict)

if __name__ == '__main__':
    data = {'name': 'John', 'friends': [{'name': 'Alice'}, {'name': 'Bob'}]}
    query = dict_to_field({'name': None, 'friends': {'name': None}})
    print(query.execute(data))
    print(query.fields)
