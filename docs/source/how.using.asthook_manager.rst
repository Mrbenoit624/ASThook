==================
asthook-manager
==================

Usage
#####

::

  usage: asthook-manager [-h] {list,remove,start_server,stop_server} ...

  Asthook manager
  
  optional arguments:
    -h, --help            show this help message and exit
  
  service:
    {list,remove,start_server,stop_server}
      list                list project
      remove              remove project
      start_server        start server
      stop_server         stop server

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
