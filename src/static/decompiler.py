import os
import subprocess
import apk2java

class Decompiler:
    def __init__(self, app, tmp_dir, args):
        self.__app = app
        self.__tmp_dir = tmp_dir
        self.__args = args
        if self.__args.decompiler == 'none' and \
            os.path.exists("%s/decompiled_app/%s" % (self.__tmp_dir,
                self.__app.split('/')[-1])):
            return
        subprocess.call(["rm", "-rf", "%s/decompiled_app/%s" % (self.__tmp_dir,
                self.__app.split('/')[-1])])
        if self.__args.decompiler == 'cfr' or self.__args.decompiler == 'procyon':
           subprocess.call(["src/submodule/apkx/apkx", self.__app, "-d",
               self.__args.decompiler])
           dir_extract = "%s/decompiled_app/%s" % (self.__tmp_dir,
                   self.__app.split('/')[-1])
           app = os.path.splitext(self.__app.split('/')[-1])[0]
           #subprocess.call(["unzip", self.__app, "-d", dir_extract + "/zip/"])
           subprocess.call(["mv", app, dir_extract])
           subprocess.call(["apktool", "d", self.__app, "-o", dir_extract +
           "/apktools"])
           subprocess.call(["cp", dir_extract + "/apktools/AndroidManifest.xml",
               dir_extract])
           #subprocess.call(["rm", "-rf", dir_extract])
           #subprocess.call(["mkdir", dir_extract + "/zip" ])
           #subprocess.call(["cp", dir_extract + "/AndroidManifest.xml",
           #    dir_extract + "/zip/" ])
        else:
            apk2java.decompile(self.__app, "%s/decompiled_app" % self.__tmp_dir)
