How to Install
==============

prerequisite
*************

You need to have on your system these package installed:

* git
* python3
* python3-pip
* liblzma5
* apktool


installation
************

If you want to install from source or have a clean development environment.
I advise you to use a virtualenv_ and follow theses command:



.. _virtualenv: https://python-guide-pt-br.readthedocs.io/fr/latest/dev/virtualenvs.html

.. code-block:: bash

   git clone --recursive -j8 https://gitlab.com/MadSquirrels/mobile/asthook.git
   cd asthook
   pip3 install -r requirements.txt
   python3 setup.py install

If you have an easy installation use install and unistall script:

.. code-block:: bash

   git clone --recursive -j8 https://gitlab.com/MadSquirrels/mobile/asthook.git
   cd asthook
   ./install.sh


Setup sdktools:
***************

.. code-block:: bash

   wget https://dl.google.com/android/repository/commandlinetools-linux-6200805_latest.zip
   mkdir <sdktoolspath>
   cd <sdktoolspath>
   unzip commandlinetools-linux-6200805_latest.zip

Install the minimum with the correct version when I written that it's look like
that:

.. code-block:: bash

  cd <sdktools>
  tools/bin/sdkmanager "platform-tools" "platforms;android-30" "build-tools;30.0.2" "emulator" --sdk_root=.

.. warning::

  If an error you can check the list of package available and update it

.. code-block:: bash
  
  cd <sdktools>
  tools/bin/sdkmanager --list --sdk_root=.

.. asciinema:: sdkmanager.cast
  :preload:

Setup decompiler Jadx:

.. code-block:: bash

   cd src/submodule/jadx
   ./gradlew dist


Documuentation
##############

Make this documentation:

.. code-block:: bash

   cd docs
   pip3 install -r requirement.txt
   make render
