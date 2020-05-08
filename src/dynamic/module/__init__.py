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
        self.__tmp_dir = tmp_dir
        self.__list_module_loaded = {}
        self.__args = args

        for name, desc, func, action, nargs in get_dynamic_modules():
            if args.__dict__[name] or args.__dict__[name] == []:
                self.__list_module_loaded[name] = func(frida, device, tmp_dir, args)

    def load(self, module, args=None):
        self.load_module()
        for name, desc, func, action, nargs in get_dynamic_modules():
            if name == module:
                if module in self.__list_module_loaded:
                    self.unload(module)
                if args:
                    test = self.__args
                    exec("test.%s = %s" % (module, args))
                self.__list_module_loaded[name] = func(self.__frida,
                                                       self.__device,
                                                       self.__tmp_dir,
                                                       self.__args)

    def unload(self, module):
        if module in self.__list_module_loaded:
            del self.__list_module_loaded[module]

    def unload_all(self):
        self.__list_module_loaded.clear()

    def reload(self):
        for module, func in self.__list_module_loaded.items():
            self.unload(module)
            self.load(module)

    def load_module(self):
        for i in Path(__file__).parent.absolute().glob('*.py'):
            if i.name != "register.py" and i.name != "__init__.py":
                __import__("dynamic.module.%s" % i.stem)

    def get_modules_list(self):
        return [ module for module, func in self.__list_module_loaded.items()]




