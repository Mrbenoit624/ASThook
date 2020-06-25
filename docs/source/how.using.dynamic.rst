Dynamic Mode
============

On the dynamic mode the tool allow to be run on the material phone or on a
emulator.

.. warning:: 
  Becareful if you use a material phone the binary frida-server on
  `bin/frida-server` should be replace by an arm version
  `<https://github.com/frida/frida/releases>`_

Launch your first dynamic analysis
##################################

On emulator
***********

Options needed to works are:

- phone: is the name given by the avdmanager when you create the virtual phone
  to list your available phone:
.. code-block:: bash

  <sdktools>/emulator/emulator -list-avds
- sdktools: the path you should specify is the same where you install the
  sdktools during the `setup </how.install.html>`_

On material
***********

Options needed to works are:

- phone: is the name of your phone you can obtain it with 
.. code-block:: bash

  adb devices
- no-emulation: no parameter only to precise to not used the emulator

Analyse an apk and its environment
##################################

Multi apk
*********

If you have for an analysis an apk which can't works without some other apk you
can setup this environment automatically thanks to `--env_apks`

Plugins
#######

To use plugins available each plugin should have a documentation you can found
all plugins available here:

.. toctree::
  :maxdepth: 1
  :titlesonly:
  :glob:

  dynamic.module.*
