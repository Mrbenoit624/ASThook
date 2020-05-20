from static.ast import Node
import re
from utils import Output

@Node("MethodDeclaration", "in")
class MethodDeclaration:
    @classmethod
    def call(cls, r, self):
        if r["list_funcs_class"] and re.search(Func.get_name(), self.elt.name):
            fc = "%s.%s" % (r["list_funcs_class"], self.elt.name)
            Output.add_tree_mod("list_funcs", "func", [
                "%s%s" % (fc, " " * (80 - len(fc))),
                r["package"]])
        return r

@Node("ConstructorDeclaration", "in")
class ClassDeclarationIn:
    @classmethod
    def call(cls, r, self):
        if r["list_funcs_class"] and re.search(Func.get_name(), self.elt.name):
            fc = "%s.%s" % (r["list_funcs_class"], self.elt.name)
            Output.add_tree_mod("list_funcs", "func", [
                "%s%s" % (fc, " " * (80 - len(fc))),
                r["package"]])
        return r

@Node("ClassDeclaration", "in")
class ClassDeclaration:
    @classmethod
    def call(cls, r, self):
        if re.search(Class.get_name(), self.elt.name):
            r["list_funcs_class"] = self.elt.name
        return r

@Node("ClassDeclaration", "out")
class ClassDeclaration:
    @classmethod
    def call(cls, r, self):
        r["list_funcs_class"] = ""
        return r

@Node("File", "in")
class File:
    @classmethod
    def call(cls, r, path):
        r["list_funcs_class"] = ""
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

