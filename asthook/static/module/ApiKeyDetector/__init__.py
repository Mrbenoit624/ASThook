
from asthook.static.module.register import ModuleStaticCmd, load_module
from asthook.utils import Output
#from Logger import debug
from asthook.log import debug
from pathlib import Path
import xml.etree.ElementTree as ET

@ModuleStaticCmd("api_keys", "find api keys", bool)
class Tree:
    """
    Find API keys
    """
    def __init__(self, package, tmp_dir, args):
        #for e in logging.root.manager.loggerDict:
        #    logging.getLogger(e).setLevel(logging.ERROR)
        from api_key_detector import detector
        load_module("ApiKeyDetector", "keys")
        load_module("name_file", "name_file_node")
        #hdlrs = logging.root.handlers
        #for logger in range(len(logging.root.handlers)):
        #    if type(hdlrs[logger]) is logging.StreamHandler:
        #        hdlrs.pop(logger)
        #        break
        path_res = Path(tmp_dir + "/decompiled_app/apktools/res")
        string_file = Path(str(path_res) + "/values/strings.xml")
        Output.add_printer_callback("tree", "ApiKeyDetector", "Manifest", mprint)
        Output.add_printer_callback("tree", "ApiKeyDetector", "source-code", mprint)
        if string_file.is_file():
            tree = ET.parse(string_file)
            strings = tree.getroot().findall('string')
            for s in strings:
                try:
                    if detector.detect_api_keys([s.text])[0]:
                        Output.add_tree_mod("ApiKeyDetector", "Manifest",
                                [s.get('name'), s.text])

                        debug(f"{s.get('name')} : {s.text}")
                        #print(logging.getLogger("phone_analysis"))
                        #debug(s.get("name"))
                except Exception as e:
                    pass
        from . import keys

def mprint(arg : list) -> str:
    return f"{arg[0]} : {arg[1]}"
