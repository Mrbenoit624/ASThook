import os
import shutil
import subprocess
from jinja2 import Template
from pathlib import Path
from log import warning

class GenerateAPK:

    def __init__(self, name, manifest, javafiles, args, tmp_dir):
        self.__path = "%s/poc/%s/" % (tmp_dir, name)
        self.__base = os.path.dirname(__file__) + "/base/"
        if os.path.exists(self.__path):
            shutil.rmtree(self.__path)
        Path(self.__path).mkdir(parents=True, exist_ok=True)
        shutil.copy(self.__base + "Makefile", self.__path + "Makefile")
        for javafile in javafiles:
            file = self.__path + "/java/" +javafile.get_path()
            Path(os.path.dirname(file)).mkdir(parents=True, exist_ok=True)
            with open(file, 'w') as f:
                f.write(javafile.get_content())
        with open(self.__path + manifest.get_path(), 'w') as f:
            f.write(manifest.get_content())

        if args.sdktools and args.version_android:
            with open(self.__path + "/log.out", "w") as out:
                with open(self.__path + "/log.err", "w") as err:
                    environ = os.environ
                    environ["SDK_TOOLS"] = args.sdktools
                    environ["VERSION"] = args.version_android
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

