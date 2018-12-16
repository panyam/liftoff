
from ipdb import set_trace
from pprint import pprint

class ConfigDict(object):
    def __init__(self, root):
        self.root = root

    def __getattr__(self, key, *args):
        return self.get(key, *args)

    def get(self, key, *args):
        if args:
            default_value = args[0]
            val = self.root.get(key, default_value)
        else:
            val = self.root.get(key)
        if type(val) is dict:
            val = ConfigDict(self.root)
        return val

class Config(object):
    def __init__(self, prodconfig, envconfigs):
        self._product = prodconfig
        self._envconfigs = envconfigs

        # The "current" environment
        self.curr_env = "aws"

    def print(self):
        from pprint import pprint
        print("Product Spec: ")
        pprint(self._product)

        print("Env Configs: ")
        pprint(self._envconfigs)

    @property
    def product(self):
        return ConfigDict(self._product)

    @property
    def environ(self):
        return ConfigDict(self._envconfigs[self.curr_env])

def load(path):
    """ Loads the package and environment configs of a package at a given path. """
    contents = open(path).read()
    pkgcode = compile(contents, path, "exec")
    pkgdata = {}
    exec(pkgcode, pkgdata)
    del pkgdata['__builtins__']
    return Config(pkgdata['product'], pkgdata['environments'])
