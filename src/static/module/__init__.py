
from pathlib import Path

for i in Path(__file__).parent.absolute().glob('*.py'):
    if i.name != "register.py" and i.name != "__init__.py" and \
    not str(i).endswith("node.py"):
        __import__("static.module.%s" % i.stem)

#from .tree import Tree
#from . import name_file

from .register import get_static_modules

class ModuleStatic:
    """
    Class to call function module when they are active
    """
    def __init__(self, package, tmp_dir, args):
        self.__package = package
        for name, desc, func in get_static_modules():
            if name in args.__dict__:
                func(package, tmp_dir, args)


