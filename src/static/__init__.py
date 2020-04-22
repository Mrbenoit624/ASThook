
import xml.etree.ElementTree as ET
import sys
import subprocess
import os

from utils import *
from log import Log

from static.module import ModuleStatic
from static.ast import ast
from static.decompiler import Decompiler

import apk2java

################################################################################
#
# Static Analysis
#
################################################################################
class StaticAnalysis:
    """
    Main Class to manage all static analysis
    """
    CONST_ANDROID = "{http://schemas.android.com/apk/res/android}"

    def list_activities(self):
        app = self.root.find( 'application' )
        t_all = app.findall('activity')
        t_all = t_all + app.findall('activity-alias')
        for obj in t_all:
            print(obj.attrib['%sname' % self.CONST_ANDROID])

    def Manifest(self):
        """
        Analyse the manifest
        """
        tree = ET.parse('%s/%s/%s/AndroidManifest.xml' %
                (self.__tmp_dir,
                 "decompiled_app",
                 self.__app.split('/')[-1]))
        self.root = tree.getroot()
        print(self.root.get('package'))
        self.package = self.root.get('package')
        bprint("Permission")
        for permissions in self.root.findall('uses-permission'):
            #print(permissions.attrib[0])
            name = permissions.get('%sname' % self.CONST_ANDROID)
            print(name)
        bprint("Dangerous functionnality")
        #print(root.find('application').attrib)
    
        # AllowBacup Functionality
        if not self.root.find('application').get("%sallowBackup" % self.CONST_ANDROID) == 'false':
            print(error("allowBackup: allow to backup all sensitive function on the cloud or on a pc"))
        
        # debuggable Functionality
        if self.root.find('application').get("%sdebuggable" % self.CONST_ANDROID) == 'true':
            print(error("debuggable: allow to debug the application in user mode"))
        self.list_activities()
    
    
    def __init__(self, args, tmp_dir):
        self.__app = args.app
        self.__tmp_dir = tmp_dir
        self.package = None


        bprint("Static Analysis")
        Decompiler(self.__app, self.__tmp_dir, args)
        
        self.Manifest()
        
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


