
from asthook.dynamic.module.register import ModuleDynamicCmd, BaseModuleDynamic
from asthook.utils import *
from asthook.log import debug

@ModuleDynamicCmd("anti_root", "bypass anti-root", bool)
class AntiRoot(BaseModuleDynamic):
    def _init(self):
        self.sc.append("script_frida/root_bypass.js")
        self.frida.load(self.sc[-1], "custom", self.on_message_print)
        Output.add_dynamic_mod("anti_root", "enable", False)
    
    def on_message_print(self, message, data):
        if message['type'] == 'send':
            if message['payload'] == "[root_bypass]":
                Output.get_dynamic_mod("anti_root", "enable")[0] = True
            elif message['payload'].startswith('Bypass'):
                debug(f"[anti_root] {message['payload']}")

    @classmethod
    def auto_complete(cls, args):
        return []


