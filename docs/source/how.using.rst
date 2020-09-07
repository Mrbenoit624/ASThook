============
How to Use
============

Usage:
######
::

  usage: asthook.py [-h] [--config_xxhdpi CONFIG_XXHDPI]
                     [--verbose {debug,info,warning}] [--verbose_position]
                     [--config CONFIG [CONFIG ...]]
                     [--restore_output RESTORE_OUTPUT [RESTORE_OUTPUT ...]]
                     [--output {none,json}] [--output-file OUTPUT_FILE]
                     [--sdktools SDKTOOLS] [--tree]
                     [--tree_path TREE_PATH [TREE_PATH ...]]
                     [--tree_exclude TREE_EXCLUDE [TREE_EXCLUDE ...]]
                     [--decompiler {none,jd-gui,cfr,procyon,fernflower,jadx}]
                     [--no_cache] [--progress] [--graph_ast] [--debug_ast]
                     [--seek_literal SEEK_LITERAL [SEEK_LITERAL ...]]
                     [--cloud_analysis] [--taint] [--list_read_write]
                     [--vuln_intent VULN_INTENT] [--test]
                     [--vuln_data VULN_DATA] [--simplify_graph]
                     [--provider PROVIDER] [--api_keys]
                     [--list_funcs LIST_FUNCS LIST_FUNCS] [--user_input]
                     [--gen_hook GEN_HOOK [GEN_HOOK ...]]
                     [--list_funcs_call LIST_FUNCS_CALL LIST_FUNCS_CALL]
                     [--types] [--basic_vulns] [--name_file]
                     [--env_apks ENV_APKS [ENV_APKS ...]] [--phone PHONE]
                     [--no-emulation] [--noinstall] [--proxy PROXY]
                     [--proxy_cert PROXY_CERT] [--no_erase]
                     [--nativehook NATIVEHOOK [NATIVEHOOK ...]] [--files_store]
                     [--quickhook [QUICKHOOK [QUICKHOOK ...]]] [--sslpining]
                     [--files_del]
                     app
  
  Analysis for smartphone
  
  positional arguments:
    app                   app target <filename.apk>
  
  optional arguments:
    -h, --help            show this help message and exit
    --config_xxhdpi CONFIG_XXHDPI
                          adding xxhdpi files from google api downloader
    --verbose {debug,info,warning}
                          active verbose
    --verbose_position    give verbose position
    --config CONFIG [CONFIG ...]
                          Load config file
    --restore_output RESTORE_OUTPUT [RESTORE_OUTPUT ...]
                          Load restore file
    --output {none,json}
    --output-file OUTPUT_FILE
    --sdktools SDKTOOLS   path of the sdktools for the emulation and some
                          android sdktools like the compilation of apk
  
  core_static:
    --tree                Active syntaxical analyse
    --tree_path TREE_PATH [TREE_PATH ...]
                          Analyse only a portion of apk
    --tree_exclude TREE_EXCLUDE [TREE_EXCLUDE ...]
                          Expludes directory to analyszed
    --decompiler {none,jd-gui,cfr,procyon,fernflower,jadx}
    --no_cache            disable cache and reparse all files in scope
    --progress            Display percent when it analyse static code
    --graph_ast           Draw a AST graph of the apk source code
    --debug_ast           print error encounter during the browsing of AST
  
  static:
    --seek_literal SEEK_LITERAL [SEEK_LITERAL ...]
                          seek Literal specify wit regexp
    --cloud_analysis      verify firebaseio
    --taint               taint variable node
    --list_read_write     list all read and write on filesystem
    --vuln_intent VULN_INTENT
                          found vuln intent
    --test                test
    --vuln_data VULN_DATA
                          found vuln intent deeplink
    --simplify_graph      Simplify the graph to remove all uselessnode
    --provider PROVIDER   analyse provider
    --api_keys            find api keys
    --list_funcs LIST_FUNCS LIST_FUNCS
                          list all funcs with regex as follow: --list_funcs
                          <class_regex> <function_regex>
    --user_input          list all users input
    --gen_hook GEN_HOOK [GEN_HOOK ...]
                          generate hook
    --list_funcs_call LIST_FUNCS_CALL LIST_FUNCS_CALL
                          list all funcs called with regex as follow:
                          --list_funcs_call <class_regex> <function_regex>
    --types               grab type of elements
    --basic_vulns         seek several potentials vulns
    --name_file           store the name of the file to be accessible by Node
  
  core_dynamic:
    --env_apks ENV_APKS [ENV_APKS ...]
    --phone PHONE         phones target emulator -list-avds
    --no-emulation        use a physical phone (useful for buetooth option)
    --noinstall           Application will not be installed and suggest that it
                          was already install
    --proxy PROXY         setup proxy address <ip>:<port>
    --proxy_cert PROXY_CERT
                          setup proxy address <filename>.cer
    --no_erase            no erase data of phones
  
  dynamic:
    --nativehook NATIVEHOOK [NATIVEHOOK ...]
                          hook native hook
    --files_store         store all files read or written by application
    --quickhook [QUICKHOOK [QUICKHOOK ...]]
                          give a list a js file to hook
    --sslpining           bypass all sslpining
    --files_del           prevent all files deleted


QuickStart
##########

To begin the first step is to decompile the apk:
You can choose one of these decompiler: jd-gui, cfr, procyon, fernflower, jadx

Advise
******

- cfr: quick and efficient (use apkx)
- procyon: quick and a little bit less efficient (use apkx)
- jadx: slower and make some mistake but a good alternative if these 2 first
  doesn't works
- jd-gui: very slower but less mistake and works for the most of the case
- fernflower: Not really complete

.. warning:: 
  option decompiler is needed only the first time when you already
  used it the tool get back the backup of the decompilation



.. code-block:: bash

  python3 src/analysis <apk> --decompiler <decompiler>

example:

.. code-block:: bash

  python3 src/analysis example.apk --decompiler cfr

On this example the tool create on `temp` the directory `example.apk`:

::

  └── example.apk  
      ├── decompiled_app  
      ├── dumpfile.pcap  
      └── ...  

Verbose
#######

Option verbose is really useful when tool didn't works as expected

.. code-block:: bash

  python3 src/analysis example.apk --verbose {debug, info, warning}

If you don't specify option verbose only errors will be show to you

- debug: show you all messages useful when you wrote a new plugin
- info: show you all message except debug message what I advise you if you have
  not the behavior excepted
- warning: show behavior no expected but with no incidence on your analyse

.. asciinema:: verbose.cast
  :preload:

Export Output and reinject previous analyse
###########################################

To extract data you can get back like standard output with `--output none`
parameters or in json format with `--output json` you just need after to
precise the `--output-file <file>` to store it in a file.

If you extract it in json is possible to reinject the previous analysis on the
tool to speed up the new analysis thanks to `--restore_output <file>`.

Output and input configuration files
#####################################

Load a config file and work with your team
*******************************************

To avoid a big command line is possible to create one or some yaml file will
load parameters used for the analysis.

an example of yaml file `config.yaml`

.. code-block:: yaml

  static:
    - tree: true
    - tree_path: "/com/"
  
    - gen_hook:
      - "TraceEvents.nativeDisableProviders"
    - list_funcs: 
      - '^.*'
      - '^.*'
    
  dynamic:
    - sdktools: "/usr/lib/android-sdk"
    - phone: "phone_audit2"
    - proxy: "127.0.0.1:8080"
    - proxy_cert: "misc/burp.der"
  
    - sslpining: true

In commandline this should be:

.. code-block:: bash

  python3 src/asthook.py example.apk --config config.yaml
  #
  # before:
  #
  python3 src/asthook.py example.apk --tree --tree_path /com/ --gen_hook "TraceEvents.nativeDisableProviders" --list_funcs '^.*' '^.*' --sdktools "/usr/lib/android-sdk" --phone "phone_audit2" --proxy "127.0.0.1:8080" --proxy_cert "misc/burp.der" --sslpining

You can prepare different files and load it all together:


.. code-block:: bash
  
  python3 src/asthook.py example.apk --config config.yaml config2.yaml

So it's possible to share a config file for an analyisis and load it with these
personal files.

Export analysis
***************

To export your analysis 
--output {none,json}
--output-file OUTPUT_FILE

Reuse previous analysis or external information
************************************************

To reuse a previous analysis on a new analysis or if you want to inject some
data in you can use `restore_output` option. this option will take a json file
with the same structure as in output.


.. code-block:: bash

  python3 src/asthook.py --restore_output myoutput.json

SDKTOOLS
########

Sdktools is really important if you want to emulate a phone and use the
functionality allow the tool to make some valid APK.

The path you should specify is the same where you install the sdktools during
the `setup </how.install.html>`_

Analyse an apk and its environment
##################################

Apk with different xxhdpi
*************************

If an apk have some external resources you can put in to the xxhdpi format and
pass it on arguments like that:

.. code-block:: bash

  python3 src/asthook.py example.apk --config_xxhdpi file.xxhdpi


.. code-block:: bash

  python3 src/asthook.py example.apk --env_apks apk1.apk apk2.apk

Static Mode
===========

.. toctree::
  :maxdepth: 1
  :titlesonly:
  :glob:

  how.using.static

Dynamic Mode
============

.. toctree::
  :maxdepth: 1
  :titlesonly:
  :glob:

  how.using.dynamic
