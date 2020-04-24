from static.ast import Node
from utils import *

@Node("LocalVariableDeclaration", "in")
class LocalVariableDeclaration:
    @classmethod
    def call(cls, r, self):
        if self.elt.type.name == "EditText" or \
                self.elt.type.name == "TextView":
                    Output.add_tree_mod("user_input",
                            "EditText/TextView",
                            warning("%s - %s : %s" % \
                                    (self.elt.declarators[0].name,
                                        r["Filename"],
                                        self.elt._position)))
        return r

@Node("MethodInvocation", "in")
class MethodInvocation:
    @classmethod
    def call(cls, r, self):
        return r
