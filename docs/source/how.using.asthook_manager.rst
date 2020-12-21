==================
asthook-manager
==================

Usage
#####

::

  usage: asthook-manager [-h] {list,remove,start_server,stop_server,diff} ...

  Asthook manager

  optional arguments:
    -h, --help            show this help message and exit

  service:
    {list,remove,start_server,stop_server,diff}
      list                list project
      remove              remove project
      start_server        start server
      stop_server         stop server
      diff                difference between 2 compilers or/and 2 projects

.. warning::

  If you want to use asthook-manager when you are in dev environment.
  modify `asthook-manager` and change variable DEV to True


Server
######

Server option allow user to make ast tree on another server or loacally keep in
ram a previous analyse. (on both case the analysis will be done quickly than
before)

To use it you should start the server with `asthook-manager start_server`, by
default, hostname is `localhost` and port is `6000`. But you can change it with
option `--hostname` and `--port`

Now the server was started you can use asthook with `--server <hostname>:<port>`
to launch ast analysis on the server.


List
####

Option `--list` basically list all project already analyse

Remove
######

Option `--remove <project>` basically remove project target

diff
####

Option `--diff` make possible to compare 2 APKs or/and 2 compilers

::

  usage: asthook-manager diff [-h] [--project1 PROJECT1] [--project2 PROJECT2]
                              [--decompiler1 DECOMPILER1]
                              [--decompiler2 DECOMPILER2] [--globing GLOBING]
  
  optional arguments:
    -h, --help            show this help message and exit
    --project1 PROJECT1   project1
    --project2 PROJECT2   project2
    --decompiler1 DECOMPILER1
                          decompiler1
    --decompiler2 DECOMPILER2
                          decompiler2
    --globing GLOBING     globing to include only certains files
  

When you precise only one decompiler the same will be choose for compare 2
APKs.
When you precise only one project the same will be choose for compare 2 version
of the APK.

To analyse only a part of the APK you can set a blobing path by default the
value is "**/*"
