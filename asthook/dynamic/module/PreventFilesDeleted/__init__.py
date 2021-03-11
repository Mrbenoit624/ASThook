
from asthook.dynamic.module.register import ModuleDynamicCmd, BaseModuleDynamic

import os

@ModuleDynamicCmd("files_del", "prevent all files deleted", bool)
class PreventFileDeleted(BaseModuleDynamic):
    def _init(self):
        self.sc.append("script_frida/file_del.js")
        self.frida.load(self.sc[-1], "custom",
                self.on_message)
        self.__path = "%s/files_deleted" % self.tmp_dir
        
        if not os.path.exists(self.__path):
            os.mkdir(self.__path)

    def on_message(self, message, data):
        if message['type'] == 'send':
            self.device.pull(message['payload'],
            "%s/%s" % (self.__path, os.path.basename(message['payload'])))
            print("[+] file got ")
            self.frida.post(self.sc[-1], {'type': 'input'})

    @classmethod
    def auto_complete(cls, args):
        return []
