
from ipdb import set_trace
from pprint import pprint
from liftoff import utils

def load(path):
    """ Loads the package and environment configs of a package at a given path. """
    contents = open(path).read()
    pkgcode = compile(contents, path, "exec")
    pkgdata = {}
    exec(pkgcode, pkgdata)
    del pkgdata['__builtins__']
    return utils.Object(pkgdata)
