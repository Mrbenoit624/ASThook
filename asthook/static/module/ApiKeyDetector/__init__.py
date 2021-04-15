
from asthook.static.module.register import ModuleStaticCmd, load_module
from asthook.utils import Output
from asthook.log import debug
from pathlib import Path
from asthook.utils import info

import re
import xml.etree.ElementTree as ET
import threading


@ModuleStaticCmd("api_keys", "find api keys", str, choices=["normal", "full"])
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
        Output.add_printer_callback("tree", "ApiKeyDetector", "extern-files", mprint)
        load_module("ApiKeyDetector", "keys")
        load_module("name_file", "name_file_node")
        keys.Keys_indentify.__init__()

        #return

        p = Path(tmp_dir + "/decompiled_app/").glob("**/*")
        for string_file in p:
            if not string_file.is_file():
                continue
            if string_file.match("**/res/drawable*/**"):
                continue

            thread = threading.Thread(target = self.analyse, args = (string_file, tmp_dir, whitelist_extension))
            thread.start()

    def analyse(self, string_file, tmp_dir, whitelist_extension):

            #Output.add_printer_callback("tree", "ApiKeyDetector", str(string_file), mprint)

            failed = True
            if '.xml' in string_file.suffixes:
                try:
                    tree = ET.parse(string_file)
                    strings = tree.getroot().findall('string')
                    for s in strings:
                        n_path = string_file.relative_to(tmp_dir + "/decompiled_app/")
                        if keys.Keys_indentify.match(s.text,
                                f"$PATH_APP/{n_path}",
                                False):
                            continue
                        try:
                            if detector.detect_api_keys([s.text])[0]:
                                Output.add_tree_mod("ApiKeyDetector",
                                "extern-files",
                                [s.text, f"$PATH_APP/{n_path}"])
                                debug(f"{n_path} : {s.get('name')} : {s.text}")
                        except Exception as e:
                            pass
                except ET.ParseError as e:
                    failed = False

            
            # Let's handle classic file from the whitelist extension
            if failed and (not string_file.suffixes or string_file.suffixes[0] in whitelist_extension):
                with open(string_file, 'rb') as f:
                    data = f.read()

                quoted = re.compile('"[^"]*"')
                for value in quoted.findall(str(data)):
                    n_path = string_file.relative_to(tmp_dir + "/decompiled_app/")
                    if keys.Keys_indentify.match(value[1:-1],
                            f"$PATH_APP/{n_path}",
                            False):
                        continue
                    try:
                        value = value[1:-1]
                        if detector.detect_api_keys([value])[0]:
                            Output.add_tree_mod("ApiKeyDetector",
                            "extern-files",
                            [value, f"$PATH_APP/{n_path}"])
                            debug(f"{n_path} : {value}")
                    except Exception as e:
                        pass

def mprint(arg : list) -> str:
    if len(arg) <= 2:
        return f"[ {arg[0]} ] : {arg[1]}"
    else:
        return f"[ {arg[0]} ] : {arg[1]} ! {info(arg[2])}"
