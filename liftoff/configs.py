
import yaml
from ipdb import set_trace
from pprint import pprint
from liftoff import utils

class Appliance(object):
    """ An appliance is a contained set of logical resources that are distributed, 
    deployed and launched as a "stack". """
    config_path = ""

    def __init__(self, **configs):
        self.configs = utils.ensure_object(configs)
        self.name = self.configs.name
        self.version = self.configs.version
        self.resources = {r['name']: Resource(**r) for r in configs['resources']}

class Resource(object):
    """ A resource required by an appliance. """
    def __init__(self, **configs):
        self.configs = utils.ensure_object(configs)
        self.name = configs["name"]
        self.providers = utils.ensure_object(configs.get('providers', {}))
        self.bootstrap_script = utils.ensure_object(configs.get('bootstrap', []))

def load(path):
    """ Loads the package and environment configs of a package at a given path. """
    contents = open(path).read()
    if path.endswith(".yaml"):
        pkgdata = yaml.load(contents)
    else:
        pkgcode = compile(contents, path, "exec")
        pkgdata = {}
        exec(pkgcode, pkgdata)
        del pkgdata['__builtins__']
    set_trace()
    appliance = Appliance(**(pkgdata['appliance']))
    appliance.config_path = path
    return appliance
