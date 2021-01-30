
import sys
import subprocess
import os

from asthook.utils import *
from asthook.log import Log

from asthook.static.module import ModuleStatic
from asthook.static.ast import ast
from asthook.static.decompiler import Decompiler
from asthook.static.manifest import Manifest


################################################################################
#
# Static Analysis
#
################################################################################
class StaticAnalysis:
    """
    Main Class to manage all static analysis
    """
   
    
    def __init__(self, args, tmp_dir):
        self.__app = args.app
        self.__tmp_dir = tmp_dir
        self.__basepath = '%s/%s/' % (
                self.__tmp_dir,
                self.__app.split('/')[-1])
        self.__basepathdecompile = '%s/%s/' % (
                self.__basepath,
                "decompiled_app")
        self.manifest = None

        bprint("Static Analysis")

        if os.path.exists(self.__app):
            Decompiler(self.__app, self.__basepathdecompile, args)
        elif not os.path.exists(f"{self.__basepathdecompile}"):
            print(f"{self.__basepathdecompile}")
            sys.stderr.write("Application doesn't exist\n")
            sys.exit(1)

        packages = []
        if args.env_apks:
            for apk in args.env_apks:
                basepathdecompile = "%s/%s/%s/" % (
                        self.__tmp_dir,
                        apk.split('/')[-1],
                        "decompiled_app")
                Decompiler(apk, basepathdecompile, args)
                packages.append([apk, 
                    Manifest('%s/AndroidManifest.xml' %
                        (basepathdecompile)
                        ).package])
            args.env_apks = packages



        self.manifest = Manifest('%s/AndroidManifest.xml' %
                (self.__basepathdecompile))

        modules = ModuleStatic(self.__app, "%s" % (self.__basepath), args)

        if args.tree:
            bprint("Tree analysis")
            print(info("PATH_SRC = %s/src" % \
                    (self.__basepathdecompile)))
            if args.server:
                self.parse_server(args)
            else:
                ast(self.__basepath, self.__app, args)
        if args.progress:
            print('\r', end='')
        Output.print_static_module()
        #UserInput(app)
        #subprocess.call(["rm", "-rf", "%s/decompiled_app" % DIR], shell=False)
    
    def parse_server(self, args):
        from multiprocessing.connection import Client
        import pickle
    
        server = args.server.split(':')
        address = (server[0], int(server[1]))
        conn = Client(address, authkey=b'madkey')
        conn.send('args')
        conn.send(pickle.dumps(args))
        if not conn.recv() == "args OK":
            return
        conn.send('output')
        conn.send(pickle.dumps(Output.get_store()))
        if not conn.recv() == "output OK":
            return
        conn.send('run')
        
        while True:
            mess = conn.recv()
            if mess == "progress":
                print(f"\r{conn.recv()}%", end='')
            else:
                print(f"\n{mess}")
                break

        conn.send('close')
        conn.close()


