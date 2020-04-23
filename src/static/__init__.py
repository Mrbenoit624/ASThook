
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
        self.manifest = None


        bprint("Static Analysis")
        Decompiler(self.__app, self.__tmp_dir, args)
        
        self.manifest = Manifest('%s/%s/%s/AndroidManifest.xml' %
                (self.__tmp_dir,
                 "decompiled_app",
                 self.__app.split('/')[-1]))
        
        modules = ModuleStatic(self.__app, self.__tmp_dir, args)
        
        if args.tree:
            bprint("Tree analysis")
            print(info("PATH_SRC = %s/decompiled_app/%s/src" % \
                    (self.__tmp_dir, self.__app.split('/')[-1])))
            ast(self.__tmp_dir, self.__app, args)
        Output.print_static_module()
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(Output.dump(args.output))
        #UserInput(app)
        #subprocess.call(["rm", "-rf", "%s/decompiled_app" % DIR], shell=False)


