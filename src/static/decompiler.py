import os
import subprocess
import apk2java

class Decompiler:
    def __init__(self, app, base_path, args):
        self.__app = app
        self.__args = args
        self.__dir_extract = base_path
        if self.__args.decompiler == 'none' and \
                os.path.exists(self.__dir_extract):
            return
        subprocess.call(["rm", "-rf", self.__dir_extract])
        if self.__args.config_xxhdpi:
            subprocess.call(["unzip", "-o", self.__args.config_xxhdpi, "-d",
                self.__dir_extract ])
        if self.__args.decompiler == 'cfr' or self.__args.decompiler == 'procyon':
           subprocess.call(["src/submodule/apkx/apkx", self.__app, "-d",
               self.__args.decompiler])
           app = os.path.splitext(self.__app.split('/')[-1])[0]
           #subprocess.call(["unzip", self.__app, "-d", dir_extract + "/zip/"])
           subprocess.call(["mv", app, self.__dir_extract])
           subprocess.call(["apktool", "d", self.__app, "-o", self.__dir_extract +
           "/apktools"])
           subprocess.call(["cp", self.__dir_extract + "/apktools/AndroidManifest.xml",
               self.__dir_extract])
           #subprocess.call(["rm", "-rf", dir_extract])
           #subprocess.call(["mkdir", dir_extract + "/zip" ])
           #subprocess.call(["cp", dir_extract + "/AndroidManifest.xml",
           #    dir_extract + "/zip/" ])
        else:
            apk2java.decompile(self.__app, self.__dir_extract)
