
from static.module.register import ModuleStaticCmd
from utils import Output
#from Logger import debug
from log import debug
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
        from . import keys
        from ..name_file import name_file_node
        #hdlrs = logging.root.handlers
        #for logger in range(len(logging.root.handlers)):
        #    if type(hdlrs[logger]) is logging.StreamHandler:
        #        hdlrs.pop(logger)
        #        break
        path_res = Path(tmp_dir + "/decompiled_app/apktools/res")
        string_file = Path(str(path_res) + "/values/strings.xml")
        if string_file.is_file():
            tree = ET.parse(string_file)
            strings = tree.getroot().findall('string')
            for s in strings:
                try:
                    if detector.detect_api_keys([s.text])[0]:
                        debug(f"{s.get('name')} : {s.text}")
                        #print(logging.getLogger("phone_analysis"))
                        #debug(s.get("name"))
                except Exception as e:
                    pass
        from . import keys

def mprint(arg : list) -> str:
    ret = f"{arg[0]}"
    for i in arg[1]:
        ret+= f"\n\t{i}"
    return ret
