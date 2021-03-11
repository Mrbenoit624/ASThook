
from asthook.dynamic.module.register import ModuleDynamicCmd, BaseModuleDynamic
from asthook.utils import Output
from asthook.conf import PACKAGE_PATH

@ModuleDynamicCmd("nativehook", "hook native hook", str, "+")
class NativeHook(BaseModuleDynamic):
    """
    Class to load QuickHook

    To use:
      --nativehook <name_hook> ...
      load all js scripts
    """
    def _init(self):
        for i in self.args.nativehook:
            self.sc.append("nativehook")
            with open(f"{PACKAGE_PATH}/script_frida/hooknative.js") as f:
                test = f.read()
                test += "\nJava.perform(function() {\n" \
                        "  trace(\"%s*\");\n" \
                        "});\n" % i
                self.frida.load(self.sc[-1], "custom", self.on_message_print, script=test)


    def on_message_print(self, message, data):
        if message['type'] == 'send':
            print(message['payload'])

