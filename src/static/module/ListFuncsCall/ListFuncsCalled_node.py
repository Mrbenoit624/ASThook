from static.ast import Node
import re
from utils import Output

from static.ast import ast

@Node("MethodInvocation", "in")
class MethodDeclaration:
    @classmethod
    def call(cls, r, self):
        #print("TEST")
        #print(self.elt)
        if not re.search(Func.get_name(), self.elt.member):
            return r
        qualifier = self.elt.qualifier if self.elt.qualifier else ""
        if qualifier == "":
            if type(self.parent) is ast.This:
                if type(self.parent.parent) is ast.Cast:
                    pass
#                    qualifier = self.parent.parent.elt.type.name
            elif type(self.parent) is ast.CastSelectors:
                index = self.parent.elt.index(self.elt)
                if index == 0:
                    qualifier = self.parent.parent.elt.type.name
                else:
                    pass
        if len(r["TyperMethod"]) > 0:
            list_c_types = r["TyperMethod"][-1]
            for elt in list_c_types:
                if qualifier == elt.name and \
                        not type(qualifier) is str: # TODO bug type
                    qualifier = elt.type.name
                    break
        
        function = "%s%s%s" % \
                (qualifier + "." if qualifier else "",
                    self.elt.member,
                    " " * (40 - (len(self.elt.member) + len(qualifier))))

        Output.add_tree_mod("list_funcs_called", "func", [function,
            r["Filename"], self.elt._position])
        return r

@Node("File", "in")
class File:
    @classmethod
    def call(cls, r, path):
        return r

class Func:
    @classmethod
    def set_func(cls, name):
        cls.name = name

    @classmethod
    def get_name(cls):
        return cls.name

class Class:
    @classmethod
    def set_class(cls, name):
        cls.name = name

    @classmethod
    def get_name(cls):
        return cls.name

