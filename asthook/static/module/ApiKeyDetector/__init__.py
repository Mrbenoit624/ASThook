
from asthook.static.module.register import ModuleStaticCmd, load_module
from asthook.utils import Output
from asthook.log import debug
from pathlib import Path

import re
import xml.etree.ElementTree as ET

@ModuleStaticCmd("api_keys", "find api keys", str)
class Tree:
    """
    Find API keys in source code + a list of files
    "normal" for basic analyse but sufficient
    "full" to find key anywhere
    """
    def __init__(self, package, tmp_dir, args):
        from api_key_detector import detector

        whitelist_extension = ['.js', '.xml', '.properties', '.txt']
        if args.api_keys == "full":
            whitelist_extension.append('.smali')


        Output.add_printer_callback("tree", "ApiKeyDetector", "source-code", mprint)
        load_module("ApiKeyDetector", "keys")
        load_module("name_file", "name_file_node")

        #return

        p = Path(tmp_dir + "/decompiled_app/").glob("**/*")
        for string_file in p:
            failed = True
            if not string_file.is_file():
                continue
            if string_file.match("**/res/drawable*/**"):
                continue

            Output.add_printer_callback("tree", "ApiKeyDetector", str(string_file), mprint)

            if '.xml' in string_file.suffixes:
                try:
                    tree = ET.parse(string_file)
                    strings = tree.getroot().findall('string')
                    for s in strings:
                        try:
                            if detector.detect_api_keys([s.text])[0]:
                                Output.add_tree_mod("ApiKeyDetector", str(string_file), [s.get('name'), s.text])
                                debug(f"{string_file.absolute()} : {s.get('name')} : {s.text}")
                        except Exception as e:
                            pass
                except ET.ParseError as e:
                    failed = False

            
            # Let's handle classic file from the whitelist extension
            if failed and (not string_file.suffixes or string_file.suffixes[0] in whitelist_extension):
                f = open(string_file, 'rb')
                data = f.read()
                f.close()

                quoted = re.compile('"[^"]*"')
                for value in quoted.findall(str(data)):
                    try:
                        value = value[1:-1]
                        if detector.detect_api_keys([value])[0]:
                            Output.add_tree_mod("ApiKeyDetector", str(string_file), ["", value])
                            debug(f"{string_file.absolute()} : {value}")
                    except Exception as e:
                        pass

def mprint(arg : list) -> str:
    return f"{arg[0]} : {arg[1]}"
