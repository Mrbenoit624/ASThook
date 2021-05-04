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
* adb

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

You should add ANDROID_SDK_ROOT environment variable with <sdktoolspath>

For bash:

.. code-block:: bash

  echo 'export ANDROID_SDK_ROOT=<sdktoolspath>' >> ~/.bashrc

For Fish:

.. code-block:: fish

  echo "set -x ANDROID_SDK_ROOT <sdktoolspath>" >> ~/.config/fish/config.fish

I advise you to update your sdkmanager environment and accept licenses with
theses commands:

.. code-block:: bash

  sdkmanager --update
  sdkmanager --licenses

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

To create an virtual phone without android studio you can use avdmanager
command. Becareful, if you wanted a rooted phone you should not use a phone
with google api.

Examples:

.. code-block:: bash

  # Not rooted phone with android 25
  sdkmanager 'system-images;android-25;google_apis;x86_64'
  avdmanager create avd --force --name not_rooted_phone --abi google_apis/x86_64 --package 'system-images;android-25;google_apis;x86_64'

  # Rooted phone with android 25
  sdkmanager 'system-images;android-25;default;x86_64'
  avdmanager create avd --force --name rooted_phone --abi default/x86_64 --package 'system-images;android-25;default;x86_64'

You can now list your virtual phone:

.. code-block:: bash

  avdmanager list avd



Documuentation
##############

Make this documentation:

.. code-block:: bash

   cd docs
   pip3 install -r requirement.txt
   make render
