
import sys
import subprocess
import os

from utils import *
from log import Log

from static.module import ModuleStatic
from static.ast import ast
from static.decompiler import Decompiler
from static.manifest import Manifest


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

        if not os.path.exists(self.__app):
            sys.stderr.write("Application doesn't exist\n")
            sys.exit(1)


        bprint("Static Analysis")
        Decompiler(self.__app, self.__basepathdecompile, args)
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
            ast(self.__basepath, self.__app, args)
        Output.print_static_module()
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(Output.dump(args.output))
        #UserInput(app)
        #subprocess.call(["rm", "-rf", "%s/decompiled_app" % DIR], shell=False)


