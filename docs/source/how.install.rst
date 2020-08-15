How to Install
==============

To install all dependencies you should use:

.. code-block:: bash

   git clone --recursive -j8 https://gitlab.com/MadSquirrels/mobile/asthook.git
   cd asthook
   pip3 install -r requirement.txt
   apt install apktool

Setup sdktools:

.. code-block:: bash

   wget https://dl.google.com/android/repository/commandlinetools-linux-6200805_latest.zip
   mkdir <sdktoolspath>
   cd <sdktoolspath>
   unzip commandlinetools-linux-6200805_latest.zip

Install the minimum with the correct version when I written that it's look like
that:

.. code-block:: bash

  cd <sdktools>
  tools/bin/sdkmanager "platform-tools" "platforms;android-R" "build-tools;30.0.0-rc4" "emulator" --sdk_root=.

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
