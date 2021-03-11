
from asthook.dynamic.module.register import ModuleDynamicCmd, BaseModuleDynamic
from asthook.utils import Output
from asthook.log import error


@ModuleDynamicCmd("shell", "give a command to execute", str, "+")
class Shell(BaseModuleDynamic):
    """
    Class to load QuickHook

    To use:
      --shell <command> <command> ...
    """
    def _init(self):
        i = "script_frida/shell.js"
        self.sc.append(i)
        ret, e = self.frida.load(i, "custom", self.on_message_print)
        command = " ".join(self.args.shell)
        self.frida.post(i, {'type' :'command', 'payload': command})


    def on_message_print(self, message, data):
        if message['type'] == 'send' and 'payload' in message:
            print(message['payload'])
        elif message['type'] == 'error':
            error(message['description'])
            error(message['stack'])
            self.is_alive = False
