
from .register import ModuleDynamicCmd

@ModuleDynamicCmd("sslpining", "bypass all sslpining")
class SSLpinning:
    def __init__(self, frida, device, tmp_dir, args):
        frida.load("script_frida/sslpinning.js", "print")
