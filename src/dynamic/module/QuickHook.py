
from .register import ModuleDynamicCmd

@ModuleDynamicCmd("quickhook", "give a list a js file to hook", "str")
class QuickHook:
    """
    Class to load QuickHook

    To use:
      --quickhook <script>,<script>
      load all js scripts
    """
    def __init__(self, frida, device, tmp_dir, args):
        self.__frida = frida
        self.__sc = []
        for i in args.quickhook.split(","):
            self.__sc.append(i)
            self.__frida.load(i, "print")
    
    def __del__(self):
        for i in self.__sc:
            self.__frida.unload(i)
