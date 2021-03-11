from asthook.log import debug
import os

modules = []

class ModuleDynamicCmd:
    def __init__(self, name, desc, action, nargs=1):
        self.name = name
        self.desc = desc
        self.action = action
        self.nargs = nargs
    def __call__(self, func):
        modules.append((self.name, self.desc, func, self.action, self.nargs))
        return func

class BaseModuleDynamic:

    def __init__(self, frida, device, tmp_dir, args, name):
        self.__frida = frida
        self.__tmp_dir = tmp_dir
        self.__device = device
        self.__args = args
        self.__name = name
        self.sc = []
        self._init()
        debug(f"[{self.__name}] module loaded")

    def _init(self):
        pass

    @property
    def frida(self):
        return self.__frida

    @property
    def tmp_dir(self):
        return self.__tmp_dir

    @property
    def device(self):
        return self.__device

    @property
    def args(self):
        return self.__args

    @property
    def is_alive(self):
        return self._is_alive if "_is_alive" in self.__dict__ else True
    
    @is_alive.setter
    def is_alive(self, alive):
        self._is_alive = alive

    @classmethod
    def auto_complete(cls, args):
        return cls.auto_complete_fs(args)

    @classmethod
    def auto_complete_fs(cls, args):
        if len(args) == 0:
            args = ['./']
        if os.path.isfile(args[-1]):
            args.append('./')
        dir, part, base = args[-1].rpartition('/')
        if part == '':
            dir = './'
        elif dir == '':
            dir = '/'

        completions = []
        for f in os.listdir(dir):
            if f.startswith(base):
                if os.path.isfile(os.path.join(dir,f)):
                    completions.append(f)
                else:
                    completions.append(f+'/')

        return completions

    def remove(self):
        for i in self.sc:
            self.__frida.unload(i)
        self._remove()
        debug(f"[{self.__name}] module unloaded")

    def _remove(self):
        pass

    def __del__(self):
        pass

def get_dynamic_modules():
    return modules
