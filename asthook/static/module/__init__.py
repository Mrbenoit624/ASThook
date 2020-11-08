
from pathlib import Path

for i in [x for x in Path(__file__).parent.absolute().iterdir() if x.is_dir()]:
    __import__("asthook.static.module.%s" % i.stem)


from .register import get_static_modules

class ModuleStatic:
    """
    Class to call function module when they are active
    """
    def __init__(self, package, tmp_dir, args):
        self.__package = package
        for name, desc, func, action, nargs, choices in get_static_modules():
            if name in args.__dict__ and \
                    (args.__dict__[name] or args.__dict__[name] == []):
                func(package, tmp_dir, args)


