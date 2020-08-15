Make a dynamic module
=====================

For a dynamic module you need to use the decorator `@ModuleDynamicCmd`

.. code-block:: python

  @ModuleDynamicCmd("sslpining", "bypass all sslpining", bool)

The following example show how to make a basic module

.. code-block:: python

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

The constructor of the class give access to:

- Frida object: to interact with frida server
- my_adb object: to interact with the device thanks to adb command
- tmp_dir str: to give the path where all files of this project is store
- args object: to give all arguments give by user at launch or on the
  interactive mode.

Some option can be intersting to use:

.. toctree::
  :maxdepth: 1
  :titlesonly:
  :glob:

  how.contribute.module.dynamic.*

