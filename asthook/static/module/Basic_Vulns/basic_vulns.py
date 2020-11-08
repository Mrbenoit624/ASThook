from asthook.static.ast import Node
from asthook.utils import *

@Node("File", "in")
class File:
    @classmethod
    def call(cls, r, path):
        for i in r["imports"]:
            if "java.util.Random" == i.path:
                Output.add_tree_mod("basic_vulns", "Unsecure Random",
                        r["Filename"], r["instance"])
        return r
