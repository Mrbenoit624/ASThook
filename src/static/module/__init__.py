from .tree import Tree

from .register import get_static_modules
from . import *

class ModuleStatic:
    def __init__(self, package, tmp_dir, args):
        self.__package = package
        for name, desc, func in get_static_modules():
            if name in args.__dict__:
                func(package, tmp_dir, args)


