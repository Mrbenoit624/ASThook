
import xml.etree.ElementTree as ET
import sys
import subprocess
import os

from utils import *
from log import Log

from static.module import ModuleStatic
from static.ast import ast

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

    def Manifest(self):
        """
        Analyse the manifest
        """
        tree = ET.parse('%s/%s/%s/AndroidManifest.xml' %
                (self.__tmp_dir,
                 "decompiled_app",
                 self.__app.split('/')[-1]))
        root = tree.getroot()
        print(root.get('package'))
        self.package = root.get('package')
        bprint("Permission")
        for permissions in root.findall('uses-permission'):
            #print(permissions.attrib[0])
            name = permissions.get('%sname' % self.CONST_ANDROID)
            print(name)
        bprint("Dangerous functionnality")
        #print(root.find('application').attrib)
    
        # AllowBacup Functionality
        if not root.find('application').get("%sallowBackup" % self.CONST_ANDROID) == 'false':
            print(error("allowBackup: allow to backup all sensitive function on the cloud or on a pc"))
        
        # debuggable Functionality
        if root.find('application').get("%sdebuggable" % self.CONST_ANDROID) == 'true':
            print(error("debuggable: allow to debug the application in user mode"))
    
    #def UserInput(self):
    #    for path in Path('%s/decompiled_app' % self.__tmp_dir).rglob('*.java'):
    #        print(path)
    #        with open(path, 'r') as file:
    #            try:
    #                tree = javalang.parse.parse(file.read())
    #            except javalang.parser.JavaSyntaxError:
    #                continue
    #            l = tree.types
    #            while len(l) > 0:
    #                elt = l.pop()
    #                #print(type(elt))#.name)#__dict__)
    #                if type(elt) is javalang.tree.ClassDeclaration:
    #                    print("Class %s" % elt.name)
    #                elif type(elt) is javalang.tree.MethodDeclaration:
    #                    print("Method %s" % elt.name)
    #                elif type(elt) is javalang.tree.StatementExpression:
    #                    if type(elt.expression) is javalang.tree.Assignment:
    #                        continue
    #                    if type(elt.expression) is javalang.tree.This:
    #                        continue
    #                    if type(elt.expression) is javalang.tree.SuperConstructorInvocation:
    #                        continue
    #                    if type(elt.expression) is javalang.tree.ExplicitConstructorInvocation:
    #                        continue
    #                    if type(elt.expression) is javalang.tree.ClassCreator:
    #                        continue
    #                    if type(elt.expression) is javalang.tree.Cast:
    #                        continue
    #                    print("FunctionCall %s" % elt.expression.member)
    #                    continue
    #                elif type(elt) is javalang.tree.LocalVariableDeclaration:
    #                    for i in elt.declarators:
    #                        l.append(i)
    #                    #print(elt.__dict__)
    #                    continue
    #                elif type(elt) is javalang.tree.VariableDeclarator:
    #                    print("Variable %s" % elt.name)
    #                    continue
    #                elif type(elt) is javalang.tree.AnnotationMethod:
    #                    continue
    #                elif type(elt) is javalang.tree.ConstantDeclaration:
    #                    continue
    #                elif type(elt) is javalang.tree.FieldDeclaration:
    #                    continue
    #                elif type(elt) is javalang.tree.ReturnStatement:
    #                    continue
    #                elif type(elt) is javalang.tree.TryStatement:
    #                    continue
    #                elif type(elt) is javalang.tree.Assignment:
    #                    continue
    #                elif type(elt) is javalang.tree.IfStatement:
    #                    continue
    #                elif type(elt) is javalang.tree.SynchronizedStatement:
    #                    continue
    #                elif type(elt) is javalang.tree.ThrowStatement:
    #                    continue
    #                elif type(elt) is javalang.tree.BlockStatement:
    #                    continue
    #                elif type(elt) is javalang.tree.SwitchStatement:
    #                    continue
    #                elif type(elt) is list:
    #                    for i in elt:
    #                        l.append(i)
    #                    continue
    #                elif type(elt) is tuple:
    #                    continue
    #                if elt.body is None:
    #                    continue
    #                #print("Name %s" % elt.name)
    #                for i in elt.body:
    #                    l.append(i)
    
    #def UserInput(app):
    #   jadx = pyjadx.Jadx()
    #   app = jadx.load(app)
    #
    #   for cls in app.classes:
    #     #print(cls.name)
    #     code = cls.code.split('\n')
    #     print(cls.name)
    #     for i in range(len(code)):
    #         if "getString(" in code[i]:
    #            print("l%d: %s" % (i, code[i]))
    
    def __init__(self, args, tmp_dir):
        self.__app = args.app
        self.__tmp_dir = tmp_dir
        self.package = None


        bprint("Static Analysis")
        if not os.path.exists("%s/decompiled_app/%s" % (self.__tmp_dir,
            self.__app.split('/')[-1])):
            apk2java.decompile(self.__app, "%s/decompiled_app" % self.__tmp_dir)
            #subprocess.call(["python3", "src/submodule/apk2java-linux/apk2java.py",
            #    self.__app,
            #    "--java", "-o", "%s/decompiled_app" % self.__tmp_dir],
            #    stdout=Log.STD_OUTPOUT, stderr=Log.STD_ERR, shell=False)
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


