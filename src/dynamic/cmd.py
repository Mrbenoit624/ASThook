import cmd

from dynamic.frida import Frida
from .module.register import get_dynamic_modules

class DynCmd(cmd.Cmd):
    prompt = "frida >"

    def __init__(self, modules):
        super().__init__()
        self.modules = modules


    def emptyline(self):
        pass

    def do_EOF(self, arg):
        return self.do_exit(arg)

    def complete_load(self, text, line, begidx, endidx):
        self.modules.load_module()
        complete = [ name for name, desc, func, action in get_dynamic_modules() ]
        if not text:
            completions = complete
        else:
            completions = [ f
                            for f in complete
                            if f.startswith(text)
                            ]
        return completions

    def do_load(self, arg):
        self.modules.load(arg)

    def do_reload(self, arg):
        self.modules.reload()

    def complete_unload(self, text, line, begidx, endidx):
        complete = self.modules.get_modules_list()
        if not text:
            completions = complete
        else:
            completions = [ f
                            for f in complete
                            if f.startswith(text)
                            ]
        return completions

    def do_unload(self, arg):
        self.modules.unload(arg)

    def do_exit(self, arg):
        self.modules.unload_all()
        print("exit")
        print("You should close your emulator if it's running..")
        return True

