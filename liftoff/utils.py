
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
