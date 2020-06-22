
from static.module.register import ModuleStaticCmd
from log import debug
from pathlib import Path
import xml.etree.ElementTree as ET
import requests
from utils import Output

@ModuleStaticCmd("cloud_analysis", "verify firebaseio", bool)
class CloudAnalysis:
    """
    Class Analyse cloud

    To use:
      --cloud_analysis
    """
    def __init__(self, package, tmp_dir, args):
        Output.add_printer_callback("tree", "Cloud_analysis", "Firebase", mprint)

        path_res = Path(tmp_dir + "/decompiled_app/apktools/res")
        string_file = Path(str(path_res) + "/values/strings.xml")
        if string_file.is_file():
            tree = ET.parse(string_file)
            strings = tree.getroot().findall('string')
            for s in strings:
                if s.get("name") == "firebase_database_url":
                    url = s.text
                    r =requests.get(f"{url}/.json")
                    if not r.status_code == 401:
                        debug(f"{url}/.json is maybe vulnerable")
                        Output.add_tree_mod("Cloud_analysis", "Firebase", f"{url}/.json")
                    else:
                        debug("firebase ok")


def mprint(arg : list) -> str:
    return f"{arg}"
