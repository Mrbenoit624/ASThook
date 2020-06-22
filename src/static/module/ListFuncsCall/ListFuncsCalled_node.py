from static.ast import Node
import re
from utils import Output
from log import debug
#from static.module.Taint import taint

from static.ast import ast

taint = None

def with_taint():
    global taint
    from ..Taint import taint

@Node("MethodInvocation", "in")
class MethodInvocationIn:
    @classmethod
    def call(cls, r, self):
        #print("TEST")
        #print(self.elt)
        if not re.search(Func.get_name(), self.elt.member):
            return r
        if taint:
            #debug("")
            #debug(taint.up2Statement(self).elt)
            function = taint.revxref(taint.up2Statement(self), stop=self)
            if not function[0] == "None":
                if re.search(Class.get_name(), ".".join(function[:-1])):
                    function = ".".join(function)
                    Output.add_tree_mod("list_funcs_called", "func", [function,
                        r["Filename"], self.elt._position])
                return r
            else:
                #debug("OK")
                pass
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
        
        if not re.search(Class.get_name(), qualifier):
            return r
        function = "%s%s" % \
                (qualifier + "." if qualifier else "",
                    self.elt.member)

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

