
from asthook.dynamic.module.register import ModuleDynamicCmd
from asthook.utils import *
from asthook.log import debug

@ModuleDynamicCmd("anti_root", "bypass anti-root", bool)
class AntiRoot:
    def __init__(self, frida, device, tmp_dir, args):
        self.__frida = frida
        self.__sc = "script_frida/root_bypass.js"
        self.__frida.load(self.__sc, "custom", self.on_message_print)
        Output.add_dynamic_mod("anti_root", "enable", False)
    
    def on_message_print(self, message, data):
        if message['type'] == 'send':
            if message['payload'] == "[root_bypass]":
                Output.get_dynamic_mod("anti_root", "enable")[0] = True
            elif message['payload'].startswith('Bypass'):
                debug(f"[anti_root] {message['payload']}")

    def remove(self):
        self.__frida.unload(self.__sc)
        print("anti_root unloaded")

    def __del__(self):
        pass
        #print("ssl pinning unloaded")
