
from asthook.dynamic.module.register import ModuleDynamicCmd, BaseModuleDynamic
from asthook.utils import Output
from asthook.log import error


@ModuleDynamicCmd("quickhook", "give a list a js file to hook", str, "*")
class QuickHook(BaseModuleDynamic):
    """
    Class to load QuickHook

    To use:
      --quickhook <script> <script> ...
      load all js scripts
      if gen_hook is called hook generated will be loaded
    """
    def _init(self):
        for i in self.args.quickhook:
            self.sc.append(i)
            ret, e = self.frida.load(i, "custom", self.on_message_print, absolute=True)
            if ret == 1:
                error(f"[quickhook] file {i} doesn't exist")
            elif ret == 2:
                error(f"[quickhook] is not a file")
            elif ret == 3:
                error(f"[quickhook] {e}")
            elif ret == 4:
                error(f"[quickhook] file not valid")


        if "gen_hook" in Output.get_store()["tree"]:
            with open("/dev/shm/quickhook.js", 'w') as f:
                for i in Output.get_store()["tree"]["gen_hook"]["hook"]:
                    f.write(i[1])
            self.sc.append("/dev/shm/quickhook.js")
            self.frida.load("/dev/shm/quickhook.js", "custom",
                    self.on_message_print, absolute=True)


    def on_message_print(self, message, data):
        if message['type'] == 'send':
            print(message['payload'])
        elif message['type'] == 'error':
            error(message['description'])
            error(message['stack'])
            self.is_alive = False
