import os
import shutil
import subprocess
from jinja2 import Template
from pathlib import Path
from log import warning, error

class GenerateAPK:

    def __init__(self, name, manifest, javafiles, args, tmp_dir):
        self.__path = "%s/poc/%s/" % (tmp_dir, name)
        self.__base = os.path.dirname(__file__) + "/base/"
        if os.path.exists(self.__path):
            shutil.rmtree(self.__path)
        Path(self.__path).mkdir(parents=True, exist_ok=True)
        
        if args.sdktools and args.version_android:
            makefile = JavaFile("Makefile",
                                self.__base + "Makefile",
                                {'version' : args.version_android,
                                 'sdktools': args.sdktools})
            with open(self.__path + "Makefile", 'w') as f:
                f.write(makefile.get_content())
        else:
            shutil.copy(self.__base + "Makefile", self.__path + "Makefile")


        for javafile in javafiles:
            file = self.__path + "/java/" + javafile.get_path()
            Path(os.path.dirname(file)).mkdir(parents=True, exist_ok=True)
            with open(file, 'w') as f:
                f.write(javafile.get_content())
        with open(self.__path + manifest.get_path(), 'w') as f:
            f.write(manifest.get_content())

        if args.sdktools and args.version_android:
            if not os.path.exists(f"{args.sdktools}"):
                error("[APK_GENERATOR] The path specify for sdktools doesn't exist")
                return
            if not os.path.exists(f"{args.sdktools}/build-tools/"
                                  f"{args.version_android}"):
                error(f"[APK_GENERATOR] The path {args.sdktools}/build-tools/"
                      f"{args.version_android} doesn't exist\n"
                       "you should install it:\n"
                       "\ttools/bin/sdkmanager --install "
                      f"'build-tools;{args.version_android}'")
                return
            version_b = args.version_android.split(".")[0]
            if not os.path.exists(f"{args.sdktools}/platforms/android-{version_b}"
                                   "/android.jar"):
                error(f"[APK_GENERATOR] The path {args.sdktools}/platforms/"
                      f"android-{version_b} doesn't exist\n"
                       "you should install it:\n"
                       "\ttools/bin/sdkmanager --install "
                      f"'platforms;android-{version_b}'")
                return

            with open(self.__path + "/log.out", "w") as out:
                with open(self.__path + "/log.err", "w") as err:
                    environ = os.environ
                    #environ["SDK_TOOLS"] = args.sdktools
                    #environ["VERSION"] = args.version_android
                    proc = subprocess.Popen(['make', '-C', self.__path],
                            env=environ,
                            stdout=out,
                            stderr=err)
                    proc.wait()
        else:
            warning("APK was not build without sdktools and version_android")



class JavaFile:

    """
    path: path where write it
    template: template to used
    variable: dict : contains all variables use in file
    """
    def __init__(self, path, template, variables):
        self.__path = path
        with open(template, 'r') as f:
            template = Template(f.read())
            self.__content = template.render(variables)

    def get_path(self):
        return self.__path

    def get_content(self):
        return self.__content

