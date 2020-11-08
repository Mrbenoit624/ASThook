
from asthook.dynamic.module.register import ModuleDynamicCmd

import os

@ModuleDynamicCmd("files_del", "prevent all files deleted", bool)
class PreventFileDeleted:
    def __init__(self, frida, device, tmp_dir, args):
        self.__frida = frida
        self.__tmp_dir = tmp_dir
        self.__device = device
        self.__sc = "script_frida/file_del.js"
        self.__frida.load(self.__sc, "custom",
                self.on_message)
        self.__path = "%s/files_deleted" % self.__tmp_dir
        
        if not os.path.exists(self.__path):
            os.mkdir(self.__path)

    def on_message(self, message, data):
        if message['type'] == 'send':
            self.__device.pull(message['payload'],
            "%s/%s" % (self.__path, os.path.basename(message['payload'])))
            print("[+] file got ")
            self.__frida.post(self.__sc, {'type': 'input'})

    def __del__(self):
        self.__frida.unload(self.__sc)
