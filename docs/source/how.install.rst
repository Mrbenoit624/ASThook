How to Install
==============

To install all dependencies you should use:

.. code-block:: bash

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

   tools/bin/sdkmanager "platforms;android-R" "build-tools;30.0.0-rc4" "emulator" --sdk_root=.


Setup decompiler Jadx:

.. code-block:: bash

   cd src/submodule/jadx
   ./gradlew dist

