
from dynamic.module.register import ModuleDynamicCmd

@ModuleDynamicCmd("sslpining", "bypass all sslpining", bool)
class SSLpinning:
    def __init__(self, frida, device, tmp_dir, args):
        self.__frida = frida
        self.__sc = "script_frida/sslpinning.js"
        self.__frida.load(self.__sc, "print")

    def __del__(self):
        self.__frida.unload(self.__sc)
        print("ssl pining unloaded")