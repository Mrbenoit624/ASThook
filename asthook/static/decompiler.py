import os
import subprocess
import apk2java
from pathlib import Path
import sys
import json

from asthook.conf import PACKAGE_PATH

from asthook.log import error

class Decompiler:
    def __init__(self, app, base_path, args):
        self.__app = app
        self.__args = args
        self.__dir_extract = base_path
        if self.__args.decompiler == 'none' and \
                os.path.exists(self.__dir_extract):
            return
        if os.path.exists(self.__dir_extract):
            print('This application was already decompiled do you want to '
                  'decompiled again ? (y/N)', end=' ')
            answer = input()
            if not (answer.lower() == "y" or answer.lower() == "yes"):
                return
        info_path = Path(f"{self.__dir_extract}").parent
        info_path = info_path / "info.json"

        is_json = False
        if os.path.exists(info_path):
            is_json = True
            with open(info_path, "r") as info_file:
                info_json = json.loads(info_file.read())
                prev_decompiler = info_json['decompiler']
            with open(info_path, "w") as info_file:
                info_json['decompiler'] = self.__args.decompiler

                self.move_prev_decompilation(prev_decompiler)
                if not prev_decompiler in info_json['prev_decompiler']:
                    info_json['prev_decompiler'].append(prev_decompiler)

                info_file.write(json.dumps(info_json))

        if not is_json:
            with open(info_path, "w") as info_file:
                info_json = {'decompiler' : self.__args.decompiler,
                             'prev_decompiler' : []}
                info_file.write(json.dumps(info_json, indent=2))



        subprocess.call(["rm", "-rf", self.__dir_extract])
        if self.__args.config_xxhdpi:
            subprocess.call(["unzip", "-o", self.__args.config_xxhdpi, "-d",
                self.__dir_extract ])
        if self.__args.decompiler == 'cfr' or self.__args.decompiler == 'procyon':
           subprocess.call([f"{PACKAGE_PATH}/submodule/apkx/apkx", self.__app, "-d",
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
        elif self.__args.decompiler == "fernflower":
            subprocess.call(["apktool", "d", self.__app, "-o", self.__dir_extract +
                "/apktools"])
            subprocess.call(["unzip", self.__app, "-d", self.__dir_extract + "/zip/"])
            subprocess.call(["cp", self.__dir_extract + "/apktools/AndroidManifest.xml",
                self.__dir_extract])
            #### TODO add dex2jar ####
            for path in Path(self.__dir_extract).rglob('classes*.jar'):
                subprocess.call(["java", "-jar", f"{PACKAGE_PATH}/submodule/fernflower.jar",
                    "-ren=1", path, self.__dir_extract + "/src"])
        elif self.__args.decompiler == "jadx":
            if not os.path.exists(f"{PACKAGE_PATH}/submodule/jadx/build/jadx/bin/jadx"):
                error("Jadx is not installed\n"
                      "If you want to install it go to:\n"
                      f"\t{PACKAGE_PATH}/submodule/jadx/\n"
                      "execute ./gradlew dist")
                sys.exit(1)
            subprocess.call(["apktool", "d", self.__app, "-o", self.__dir_extract +
                "/apktools"])
            subprocess.call(["cp", self.__dir_extract + "/apktools/AndroidManifest.xml",
                self.__dir_extract])
            subprocess.call([f"{PACKAGE_PATH}/submodule/jadx/build/jadx/bin/jadx", 
                self.__app,
                "-ds",
                self.__dir_extract + "/src/"])
        else:
            apk2java.decompile(self.__app, self.__dir_extract)
            subprocess.call(["cp", self.__dir_extract + "/apktools/AndroidManifest.xml",
                self.__dir_extract])
 
    def move_prev_decompilation(self, prev_decompiler):
        prev_decomp_dir = Path(self.__dir_extract).parent / "prev_decompilation"
        if not os.path.exists(prev_decomp_dir):
           subprocess.call(["mkdir", prev_decomp_dir ])
        subprocess.call(["mv", f"{self.__dir_extract}", prev_decomp_dir / prev_decompiler ])




