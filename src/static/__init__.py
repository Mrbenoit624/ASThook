
import xml.etree.ElementTree as ET
import sys
import javalang
import subprocess
import os

#import sys
#sys.path.append("..")

from utils import bprint
from log import Log

################################################################################
#
# Static Analysis
#
################################################################################
class StaticAnalysis:
    CONST_ANDROID = "{http://schemas.android.com/apk/res/android}"

    def Manifest(self):
        tree = ET.parse('%s/%s/%s/AndroidManifest.xml' %
                (self.__tmp_dir,
                 "decompiled_app",
                 self.__app.split('/')[-1][:-4].lower()))
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
            print("allowBackup: allow to backup all sensitive function on the cloud or on a pc")
        
        # debuggable Functionality
        if root.find('application').get("%sdebuggable" % self.CONST_ANDROID) == 'true':
            print("debuggable: allow to debug the application in user mode")
    
    def UserInput(self):
        for path in Path('%s/decompiled_app' % self.__tmp_dir).rglob('*.java'):
            print(path)
            with open(path, 'r') as file:
                try:
                    tree = javalang.parse.parse(file.read())
                except javalang.parser.JavaSyntaxError:
                    continue
                l = tree.types
                while len(l) > 0:
                    elt = l.pop()
                    #print(type(elt))#.name)#__dict__)
                    if type(elt) is javalang.tree.ClassDeclaration:
                        print("Class %s" % elt.name)
                    elif type(elt) is javalang.tree.MethodDeclaration:
                        print("Method %s" % elt.name)
                    elif type(elt) is javalang.tree.StatementExpression:
                        if type(elt.expression) is javalang.tree.Assignment:
                            continue
                        if type(elt.expression) is javalang.tree.This:
                            continue
                        if type(elt.expression) is javalang.tree.SuperConstructorInvocation:
                            continue
                        if type(elt.expression) is javalang.tree.ExplicitConstructorInvocation:
                            continue
                        if type(elt.expression) is javalang.tree.ClassCreator:
                            continue
                        if type(elt.expression) is javalang.tree.Cast:
                            continue
                        print("FunctionCall %s" % elt.expression.member)
                        continue
                    elif type(elt) is javalang.tree.LocalVariableDeclaration:
                        for i in elt.declarators:
                            l.append(i)
                        #print(elt.__dict__)
                        continue
                    elif type(elt) is javalang.tree.VariableDeclarator:
                        print("Variable %s" % elt.name)
                        continue
                    elif type(elt) is javalang.tree.AnnotationMethod:
                        continue
                    elif type(elt) is javalang.tree.ConstantDeclaration:
                        continue
                    elif type(elt) is javalang.tree.FieldDeclaration:
                        continue
                    elif type(elt) is javalang.tree.ReturnStatement:
                        continue
                    elif type(elt) is javalang.tree.TryStatement:
                        continue
                    elif type(elt) is javalang.tree.Assignment:
                        continue
                    elif type(elt) is javalang.tree.IfStatement:
                        continue
                    elif type(elt) is javalang.tree.SynchronizedStatement:
                        continue
                    elif type(elt) is javalang.tree.ThrowStatement:
                        continue
                    elif type(elt) is javalang.tree.BlockStatement:
                        continue
                    elif type(elt) is javalang.tree.SwitchStatement:
                        continue
                    elif type(elt) is list:
                        for i in elt:
                            l.append(i)
                        continue
                    elif type(elt) is tuple:
                        continue
                    if elt.body is None:
                        continue
                    #print("Name %s" % elt.name)
                    for i in elt.body:
                        l.append(i)
    
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
    
    def __init__(self, app, tmp_dir):
        self.__app = app
        self.__tmp_dir = tmp_dir
        self.package = None


        bprint("Static Analysis")
        #tree = javalang.parse.parse("package javalang.brewtab.com; class Test{public void challenge_validate() {String welcome = \"Challenge Validate!\";Toast.makeText(getApplicationContext(), welcome, Toast.LENGTH_LONG).show();Intent intent = new Intent(this, ConnectActivity.class);startActivity(intent);}}")
        if not os.path.exists("%s/decompiled_app/%s" % (self.__tmp_dir,
            self.__app.split('/')[-1][:-4].lower())):
            subprocess.call(["python3", "src/submodule/apk2java-linux/apk2java.py",
                self.__app,
                "--java", "-o", "%s/decompiled_app" % self.__tmp_dir],
                stdout=Log.STD_OUTPOUT, stderr=Log.STD_ERR, shell=False)
        self.Manifest()
        #UserInput(app)
        #subprocess.call(["rm", "-rf", "%s/decompiled_app" % DIR], shell=False)

