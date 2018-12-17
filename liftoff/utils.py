
import os

def fullpath(path):
    if path[0] == '~' and not os.path.exists(path):
        path = os.path.expanduser(path)
    return os.path.abspath(path)

def ensure_pdir(path):
    path = fullpath(path)
    dirpath = os.path.dirname(path)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    assert os.path.isdir(dirpath)

def ensure_object(val):
    if type(val) is dict:
        val = Object(val)
    elif type(val) is list:
        val = Object(val)
    return val

class Object(object):
    _values = None
    def __init__(self, values):
        super().__setattr__("_values", values)

    def print(self):
        import pprint
        pprint.pprint(self._values)

    def __getitem__(self, index):
        return self.get(index)

    def __setitem__(self, index, value):
        return self.set(index, value)

    def __getattr__(self, key, *args):
        return self.get(key, *args)

    def __setattr__(self, key, value):
        return self.set(key, value)

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return ensure_object(iter(self._values))

    def get(self, key_or_index, *args):
        if type(self._values) is list:
            assert type(key_or_index) is int, "Indexing into Object list requires a slice or int"
            out = self._values[key_or_index]
        else:
            assert type(key_or_index) is str, "Indexing into Object dict requires a string key"
            if args:
                default_value = args[0]
                out = self._values.get(key_or_index, default_value)
            else:
                out = self._values.get(key_or_index)
        return ensure_object(out)

    def set(self, key_or_index, value):
        while type(value) is Object:
            value = value._values
        self._values[key_or_index] = value
