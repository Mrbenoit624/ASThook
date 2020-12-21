.. ASTHOOK documentation master file, created by
   sphinx-quickstart on Mon Jun 22 14:04:37 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: images/logo_banner.png

Welcome to ASTHOOK's documentation |version| |release|!
========================================================


Asthook allows to make a static analysis and a dynamic analysis of application
content. The great advantage of this tool is its modularity and the possibility
of teamwork. This tool brings 2 functionalities rarely highlighted is
the automated creation of APK for POC, as well as the syntax and tint analysis
of the source code.

Many plug-ins allowing to analyze the application are already present such as :
  - The search for literals in the source code
  - Lists the set of read and write functions on the file system.
  - The search for exploitable vulnerable Intent and generation of an apk poc
  - The list of all user entry points
  - The function search called in the apk
  - Function search in the apk
  - Automatic generation of a hook on a function
  - Automatic installation of the certificate
  - Automated bypass of SLL pinning
  - Recovery of deleted files
  - Etc.

At first to works the tools need to decompile and prepare the apk on the
directory `temp/<apk>`. You will can found on this directory a the apk
decompiled and some stuff put here by some plugins like wireshark trace or apk
poc built.  

The static analysis will transform the apk on a AST (Abstract Syntaxical Tree)
and do a Deth-First Search to analyse all function/variables etc.

The link of the project https://gitlab.com/MadSquirrels/mobile/asthook

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
