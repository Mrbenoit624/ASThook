
from dynamic.module.register import ModuleDynamicCmd
from utils import Output

@ModuleDynamicCmd("quickhook", "give a list a js file to hook", str, "*")
class QuickHook:
    """
    Class to load QuickHook

    To use:
      --quickhook <script> <script> ...
      load all js scripts
      if gen_hook is called hook generated will be loaded
    """
    def __init__(self, frida, device, tmp_dir, args):
        self.__frida = frida
        self.__sc = []
        for i in args.quickhook:
            self.__sc.append(i)
            self.__frida.load(i, "custom", self.on_message_print)
        if "gen_hook" in Output.get_store()["tree"]:
            with open("/dev/shm/quickhook.js", 'w') as f:
                for i in Output.get_store()["tree"]["gen_hook"]["hook"]:
                    f.write(i[1])
            self.__sc.append("/dev/shm/quickhook.js")
            self.__frida.load("/dev/shm/quickhook.js", "custom",
                    self.on_message_print)

    def on_message_print(self, message, data):
        if message['type'] == 'send':
            print(message['payload'])

    
    def __del__(self):
        for i in self.__sc:
            self.__frida.unload(i)
