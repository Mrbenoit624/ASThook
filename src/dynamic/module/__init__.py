from .GitFilesStore import GitFilesStore
from .SSLpinning import SSLpinning

from .register import get_dynamic_modules
from . import *

class ModuleDynamic:
    def __init__(self, frida, device, tmp_dir, args):
        self.__frida = frida
        self.__device = device
        for name, desc, func in get_dynamic_modules():
            if name in args.__dict__:
                func(frida, device, tmp_dir, args)


