from pathlib import Path

for i in Path(__file__).parent.absolute().glob('*.py'):
    if i.name != "register.py" and i.name != "__init__.py":
        __import__("dynamic.module.%s" % i.stem)


from .register import get_dynamic_modules
from . import *

class ModuleDynamic:
    def __init__(self, frida, device, tmp_dir, args):
        self.__frida = frida
        self.__device = device
        for name, desc, func in get_dynamic_modules():
            if args.__dict__[name]:
                func(frida, device, tmp_dir, args)


