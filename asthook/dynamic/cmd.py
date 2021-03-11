import cmd

from asthook.dynamic.frida import Frida
from .module.register import get_dynamic_modules
import time
import os

class DynCmd(cmd.Cmd):
    prompt = "asthook >"

    def __init__(self, modules, device, frida, args):
        super().__init__()
        self.__modules = modules
        self.__device = device
        self.__frida = frida
        self.__args = args


    def emptyline(self):
        pass

    def do_EOF(self, arg):
        return self.do_exit(arg)

#TODO fix complete
    def complete_load(self, text, line, begidx, endidx):
        self.__modules.load_module()
        complete = [ name for name, desc, func, action, nargs in get_dynamic_modules() ]
        line_array = line.split()
        if (len(line_array) > 2) or (len(line_array) > 1 and line_array[1] in complete):
            #print(os.listdir(text))
            return self.__modules.complete_module(line_array[1], line_array[2:])
        if not text:
            completions = complete
        else:
            completions = [ f
                            for f in complete
                            if f.startswith(text)
                            ]
        return completions

    def do_load(self, arg):
        args = arg.split()
        if len(args) > 0:
            self.__modules.load(args[0], args[1:])
        else:
            self.__modules.load(arg)

    def complete_call(self, text, line, begidx, endidx):
        return self.complete_load(text, line, begidx, endidx)
        
    def do_call(self, arg):
        args = arg.split()
        if len(args) > 0:
            self.__modules.load(args[0], args[1:])
            time.sleep(.5)
            self.__modules.unload(args[0])
        else:
            self.__modules.load(arg)
            time.sleep(.5)
            self.__modules.unload(args[0])

    def do_reload(self, arg):
        self.__modules.reload()

    def complete_unload(self, text, line, begidx, endidx):
        complete = self.__modules.get_modules_list()
        if not text:
            completions = complete
        else:
            completions = [ f
                            for f in complete
                            if f.startswith(text)
                            ]
        return completions

    def do_unload(self, arg):
        self.__modules.unload(arg)

    def do_shell(self, arg):
        #self.__device.shell("input keyevent KEYCODE_HOME")
        self.__device.shell("input keyevent KEYCODE_BACK")
        self.__device.shell(arg)
        #self.__frida.attach()
        #self.__modules.reload(self.__frida)

    def do_detach(self, arg):
        self.__args.no_emulation = True

    def do_exit(self, arg):
        self.__modules.unload_all()
        print("exit")
        print("You should close your emulator if it's running..")
        return True

