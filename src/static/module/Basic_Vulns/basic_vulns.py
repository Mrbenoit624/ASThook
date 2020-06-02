from static.ast import Node
from utils import *

@Node("File", "in")
class File:
    @classmethod
    def call(cls, r, path):
        for i in r["imports"]:
            if "java.util.Random" == i.path:
                Output.add_tree_mod("basic_vulns", "Unsecure Random",
                        [[r["Filename"],
                        "https://jazzy.id.au/2010/09/20/cracking_random_number_generators_part_1.html",
                        "It better to use java.security.SecureRandom to avoid "
                        "to predict the next random number"]])
        return r
