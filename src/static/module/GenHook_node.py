from ..ast import Node
from utils import *

@Node("MethodDeclaration", "in")
class MethodDeclaration:
    @classmethod
    def call(cls, r, self):
        if r["gen_hook_class"] and FuncToHook.get_name() == self.elt.name:
            params = ""
            args = []
            overload = ""
            prints = ""
            i=1
            if len(self.elt.parameters) > 0:
                for param in self.elt.parameters:
                    pretype = ""
                    # TODO: Vargs
                    if "Array" in param.name:
                        pretype = "[L"
                    params += " " + param.type.name
                    if param.type.name == "String":
                        args.append(("'%sjava.lang.String'" % pretype, "arg%d" % i))
                    else:
                        args.append(("", "args%d" % i))
                    i = i + 1
            if len([over for over, arg in args if over != ""]) > 0:
                overload += ".overload("
                overload += ",".join([j for j,k in args if j != ""])
                overload += ")"
            print("%s : %s" % (self.elt.name, params))
            for j, k in args:
                prints += "%ssend('%s: ' + %s);\n" % (" "*8,k,k)
            r["gen_hook_out"] =\
"Java.perform(function()\n\
{\n\
    var class_hook = Java.use('%s.%s')\n\
    class_hook.%s%s.implementation = function (%s) {\n\
        send('[+] %s.%s hooked');\n\
%s\
        var ret = this.%s(%s);\n\
        send('ret = ' + ret);\n\
        return ret\n\
    };\n\
});" % (
                r["package"], ClassToHook.get_name(),
                FuncToHook.get_name(), overload, ",".join(k for j,k in args),
                ClassToHook.get_name(), FuncToHook.get_name(),
                prints,
                FuncToHook.get_name(), ",".join(k for j,k in args));
        return r

@Node("ClassDeclaration", "in")
class ClassDeclaration:
    @classmethod
    def call(cls, r, self):
        if ClassToHook.get_name() == self.elt.name:
            r["gen_hook_class"] = True
        return r

@Node("ClassDeclaration", "out")
class ClassDeclaration:
    @classmethod
    def call(cls, r, self):
        r["gen_hook_class"] = False
        return r

@Node("File", "in")
class File:
    @classmethod
    def call(cls, r, path):
        r["gen_hook_class"] = False
        return r

@Node("Init", "out")
class End:
    @classmethod
    def call(cls, r):
        if "gen_hook_out" in r:
            print(info("*" * 32 + " Hook generated " + "*" * 32))
            print(r["gen_hook_out"])
            print(info("*"*80))
        return r

class FuncToHook:
    @classmethod
    def set_func(cls, name):
        cls.name = name

    @classmethod
    def get_name(cls):
        return cls.name

class ClassToHook:
    @classmethod
    def set_class(cls, name):
        cls.name = name

    @classmethod
    def get_name(cls):
        return cls.name

