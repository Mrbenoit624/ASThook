from pathlib import Path

for i in [x for x in Path(__file__).parent.absolute().iterdir() if x.is_dir()]:
    __import__("asthook.dynamic.module.%s" % i.stem)


from .register import get_dynamic_modules

class ModuleDynamic:
    def __init__(self, frida, device, tmp_dir, args):
        self.__frida = frida
        self.__device = device
        self.__tmp_dir = tmp_dir
        self.__list_module_loaded = {}
        self.__args = args

        for name, desc, func, action, nargs in get_dynamic_modules():
            #if args.__dict__[name] or args.__dict__[name] == []:
            if name in args.__dict__ and \
                    (args.__dict__[name] or args.__dict__[name] == []):
                self.__list_module_loaded[name] = func(frida, device, tmp_dir, args, name)

    @classmethod
    def check_module_loaded(cls, args):
        module_loaded = {}
        for name, desc, func, action, nargs in get_dynamic_modules():
            if name in args.__dict__ and \
                    (args.__dict__[name] or args.__dict__[name] == []):
                module_loaded[name] = func
        return module_loaded


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
                                                       self.__args,
                                                       name)
    def complete_module(self, module, args):
        self.load_module()
        for name, desc, func, action, nargs in get_dynamic_modules():
            if name == module:
                return func.auto_complete(args)

    def unload(self, module):
        if module in self.__list_module_loaded:
            self.__list_module_loaded[module].remove()
            del self.__list_module_loaded[module]

    def unload_all(self):
        for module in self.__list_module_loaded:
            self.__list_module_loaded[module].remove()
        self.__list_module_loaded.clear()

    def reload(self, frida = None):
        if frida:
            self.__frida = frida
        #modules = self.__list_module_loaded.copy().items()
        modules = self.get_modules_list()
        for module in modules:
            self.load(module)
        self.__frida.resume()

    def load_module(self):
        for i in Path(__file__).parent.absolute().glob('*.py'):
            if i.name != "register.py" and i.name != "__init__.py":
                __import__("dynamic.module.%s" % i.stem)

    def get_modules_list(self):
        modules = []
        for module, func in self.__list_module_loaded.copy().items():
            if not func.is_alive:
                self.unload(module)
            else:
                modules.append(module)
        return modules
