
from asthook.dynamic.module.register import ModuleDynamicCmd
from asthook.utils import Output

@ModuleDynamicCmd("nativehook", "hook native hook", str, "+")
class QuickHook:
    """
    Class to load QuickHook

    To use:
      --nativehook <name_hook> ...
      load all js scripts
    """
    def __init__(self, frida, device, tmp_dir, args):
        self.__frida = frida
        self.__sc = []
        for i in args.nativehook:
            self.__sc.append(i)
            with open("script_frida/hooknative.js") as f:
                test = f.read()
                test += "\nJava.perform(function() {\n" \
                        "  trace(\"%s*\");\n" \
                        "});\n" % i
                self.__frida.load(test, "custom", self.on_message_print)


            #self.__frida.load(test, "custom", self.on_message_print)

    def on_message_print(self, message, data):
        if message['type'] == 'send':
            print(message['payload'])

    
    def remove(self):
        for i in self.__sc:
            self.__frida.unload(i)

    def __del__(self):
        pass
