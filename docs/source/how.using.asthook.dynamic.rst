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

.. note::

  When a emulator is already launch. His beahvior is as a material devices


.. asciinema:: emulator_as_material.cast
  :preload:

.. warning::
   Becareful when you create your virtual phone I advise to choose a phone
   without google API to have a phone already rooted.

.. warning::
   If the device exist but the error no device found appear:

   I advise you to active verbose info:
   The following line can be display:

   - emulator: ERROR: Running multiple emulators with the same AVD is an experimental feature.
   To fix it you should probably:
     - check if an other instance is running
     - remove the lock file in ~/.android/avd/<avd_name>.avd/
   


On material
***********

Options needed to works are:

- phone: is the name of your phone you can obtain it with 

.. code-block:: bash

  adb devices

- no-emulation: no parameter only to precise to not used the emulator

Keep your environment safe
##########################

If your environment is already setup, you can avoid to reinstall the apk with
option `--noinstall` and if you use an emultor option `--no_erase` avoid the
default processing which clean the environment of the phone when you launch it.

.. code-block:: bash

  asthook --config config.yaml --no_erase --noinstall

Intercep https traffic with a proxy
###################################

To intercept the https traffic you can pass the parameters:

- `--proxy <address>:<port>` with address of the proxy
- `--proxy_cert <cert.der>` with the CA certificate of the proxy with der format

  For instance if you want to download your certificate and you used Burp:

  - On your computer with Burp running, visit http://burpsuite and click the
    "CA Certificate" link. Save the certificate file on your computer.

  .. figure:: images/burp_cacert.png
    :align: center
    :alt: alternate text
    :figclass: align-center



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

  plugins/dynamic/*
