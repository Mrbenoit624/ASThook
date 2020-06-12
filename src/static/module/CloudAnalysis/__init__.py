
from static.module.register import ModuleStaticCmd
from logging import debug
from pathlib import Path
import xml.etree.ElementTree as ET
import requests

@ModuleStaticCmd("cloud_analysis", "verify firebaseio", bool)
class CloudAnalysis:
    """
    Class Analyse cloud

    To use:
      --cloud_analysis
    """
    def __init__(self, package, tmp_dir, args):
        path_res = Path(tmp_dir + "/decompiled_app/apktools/res")
        debug(path_res)
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
                    else:
                        debug("firebase ok")


