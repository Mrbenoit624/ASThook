api_keys
==========

Descrition
##########

This plugins make possible to identify Api keys, ip address, hash, token, etc.

At first, some regexes identifies the most remarkable string as AWS_API_Key,
Google_API_Key etc. (full list can be found `here <https://gitlab.com/MadSquirrels/mobile/asthook/-/tree/master/asthook/static/module/ApiKeyDetector/regexes.json>`_)

Then a Neural Network Based is used to identify Automaticaly API Keys.

A Multilayer-Perceptron-based system, able to identify API Key strings with an accuracy of over 99%.

For technical details, check out my thesis (Automatic extraction of API Keys from Android applications) and, in particular, Chapter 3 of the work.

Automatic API Key detector was developed by https://github.com/alessandrodd

Usage
#####

.. code-block:: bash

  asthook <app> --api_keys <normal|full>

.. asciinema:: ApiKeyDetector.cast
  :preload:

.. asciinema:: ApiKeyDetector2.cast
  :preload:
