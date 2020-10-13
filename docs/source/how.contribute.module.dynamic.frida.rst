Frida
=====


This module allow user to interact with the frida server installed on device.

.. code-block:: python

 from dynamic.module.register import ModuleDynamicCmd

 @ModuleDynamicCmd("sslpinning", "bypass all sslpinning", bool)
 class SSLpinning:
     def __init__(self, frida, device, tmp_dir, args):
         self.__frida = frida
         self.__sc = "script_frida/sslpinning.js"
         self.__frida.load(self.__sc, "print")

     def __del__(self):
         self.__frida.unload(self.__sc)
         print("ssl pining unloaded")


To load a new frida script you should use the function `load`:

.. code-block:: python

  # To print all send message
  frida.load(self.__sc, "print")
  # To store all send message
  # use frida.get_store to get the message on the top
  frida.load(self.__sc, "store")
  # Use a custom python code to interact with frida script
  frida.load(self.__sc, "custom", function)


When the script is unload don't forget to call function unload.

.. code-block:: python

  frida.unload(self.__sc)
