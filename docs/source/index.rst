.. app_phone_analysis documentation master file, created by
   sphinx-quickstart on Mon Jun 22 14:04:37 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to app_phone_analysis's documentation!
==============================================

app_phone_analysis is another tools to analyze APK.
This tools can make a static analysis and dynamic analysis.

At first to works the tools need to decompile and prepare the apk on the
directory `temp/<apk>`. You will can found on this directory a the apk
decompiled and some stuff put here by some plugins like wireshark trace or apk
poc built.

The static analysis will transform the apk on a AST (Abstract Syntaxical Tree)
and do a Deth-First Search to analyse all function/variables etc.

How to
======

.. toctree::
  :maxdepth: 2
  :titlesonly:
  :glob:

  how

Details
=======

.. toctree::
  :maxdepth: 2
  :titlesonly:
  :glob:

  modules

.. Static
.. ======
.. 
.. 
.. .. toctree::
..   :maxdepth: 1
..   :titlesonly:
..   :glob:
.. 
..   static
.. 
.. Dynamic
.. =======
.. 
.. .. toctree::
..   :maxdepth: 1
..   :titlesonly:
..   :glob:
.. 
..   dynamic
.. 
.. Log
.. ===
.. 
.. .. toctree::
..   :maxdepth: 1
..   :titlesonly:
..   :glob:
.. 
..   log
.. 
.. Utils
.. =====
.. 
.. .. toctree::
..   :maxdepth: 1
..   :titlesonly:
..   :glob:
.. 
..   utils
.. 
.. Parser
.. ======
.. 
.. .. toctree::
..   :maxdepth: 1
..   :titlesonly:
..   :glob:
.. 
..   parser
.. 
.. Myadb
.. =====
.. 
.. .. toctree::
..   :maxdepth: 1
..   :titlesonly:
..   :glob:
.. 
..   myadb



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
