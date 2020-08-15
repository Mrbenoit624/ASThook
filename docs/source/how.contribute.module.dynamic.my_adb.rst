my_abd
======

This module allow user to interact with the device thanks to adb command

The following example show how to use it:

.. code-block:: python

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

commands available:

- shell(arg) : shell command for instance shell(ls) execute ls on device
- spawn(arg) : launch the application in arg
- push(src, dst) : push the file which are on src path on the device at path dst
- pull(src, dst) : pull the file which are on the device at src path to path dst
