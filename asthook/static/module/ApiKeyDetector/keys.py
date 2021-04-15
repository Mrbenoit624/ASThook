from asthook.static.ast import Node
from asthook.utils import Output
from asthook.log import debug
from api_key_detector import detector

import os
import json
import re



@Node("Literal", "in")
class ClassDeclarationIn:
    @classmethod
    def call(cls, r, self):
        if len(self.elt.value) > 0 and self.elt.value[0] == '"' and \
                self.elt.value[-1] == '"':
                    if Keys_indentify.match(self.elt.value[1:-1],
                            f"{r['Filename']}:{self.elt._position}"):
                        return r
                    try:
                        if detector.detect_api_keys([self.elt.value[1:-1]])[0]:
                            Output.add_tree_mod("ApiKeyDetector", "source-code",
                                    [self.elt.value[1:-1],
                                    f"{r['Filename']}:{self.elt._position}"], r["instance"])
                            debug(f"{self.elt.value} {r['Filename']}:{self.elt._position}")
                    except:
                        pass
        return r

class Keys_indentify:
    @classmethod
    def __init__(cls):
        path = f"{os.path.dirname(__file__)}/regexes.json"
        with open(path) as f:
            cls.regexes = json.load(f)

    @classmethod
    def compare(cls, pattern, string, name, path, source):
        if string is None:
            return False
        if re.match(pattern, string):
            debug(f"{path} {name} : {string}")
            Output.add_tree_mod("ApiKeyDetector",
                    "source-code" if source else "extern-files",
                    [string, path, name])
            return True
        return False

    @classmethod
    def match(cls, string, path, source=True):
        for name, pattern in cls.regexes.items():
            if type(pattern) is list:
                for p in pattern:
                    if cls.compare(p, string, name, path, source):
                        return True
            else:
                if cls.compare(pattern, string, name, path, source):
                    return True
