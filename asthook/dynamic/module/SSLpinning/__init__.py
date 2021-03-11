
from asthook.dynamic.module.register import ModuleDynamicCmd, BaseModuleDynamic

@ModuleDynamicCmd("sslpinning", "bypass all sslpinning", bool)
class SSLpinning(BaseModuleDynamic):
    def _init(self):
        self.sc.append("script_frida/sslpinning.js")
        self.frida.load(self.sc[-1], "print")

    @classmethod
    def auto_complete(cls, args):
        return []
