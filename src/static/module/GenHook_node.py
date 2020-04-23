from ..ast import Node
from utils import *

@Node("MethodDeclaration", "in")
class MethodDeclaration:
    @classmethod
    def call(cls, r, self):
        functions = FuncToHook.get_name()
        func_name = None
        class_name = None
        for i in range(0, len(r["gen_hook_class"])):
            if self.elt.name == functions[i]:
                if r["gen_hook_class"][i]:
                    func_name  = self.elt.name
                    class_name = ClassToHook.get_name()[i]
                    
        if func_name:
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
            #r["gen_hook_out"].append(\
            Output.add_tree_mod("gen_hook", "hook", ["%s.%s" % (func_name,class_name),
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
                r["package"], class_name,
                func_name, overload, ",".join(k for j,k in args),
                class_name, func_name,
                prints,
                func_name, ",".join(k for j,k in args))]);
        return r

@Node("ClassDeclaration", "in")
class ClassDeclaration:
    @classmethod
    def call(cls, r, self):
        for i in range(0, len(r["gen_hook_class"])):
            if self.elt.name == ClassToHook.get_name()[i]:
                r["gen_hook_class"][i] = True
        return r

@Node("ClassDeclaration", "out")
class ClassDeclaration:
    @classmethod
    def call(cls, r, self):
        for i in range(0, len(r["gen_hook_class"])):
            if self.elt.name == ClassToHook.get_name()[i]:
                r["gen_hook_class"][i] = False
        return r

@Node("File", "in")
class File:
    @classmethod
    def call(cls, r, path):
        r["gen_hook_class"] = []
        for i in ClassToHook.get_name():
            r["gen_hook_class"].append(False)
        return r

@Node("Init", "in")
class Begin:
    @classmethod
    def call(cls, r):
        r["gen_hook_out"] = []
        return r

@Node("Init", "out")
class End:
    @classmethod
    def call(cls, r):
        #if len(r["gen_hook_out"]) > 0:
        #    Output.add_tree_mod("gen_hook", "hook",
        #        "\n"+info("*" * 32 + " Hook generated " + "*" * 32) + "\n" +
        #        "\n\n".join(r["gen_hook_out"]) +
        #        info("\n" + "*"*80))

        #print(info("*" * 32 + " Hook generated " + "*" * 32))
        #for i in r["gen_hook_out"]:
        #    print(i, end='\n\n')
        #print(info("*"*80))
        return r

class FuncToHook:
    @classmethod
    def add_func(cls, name):
        if not "name" in cls.__dict__:
            cls.name = []
        cls.name.append(name)

    @classmethod
    def get_name(cls):
        return cls.name

class ClassToHook:
    @classmethod
    def add_class(cls, name):
        if not "name" in cls.__dict__:
            cls.name = []
        cls.name.append(name)

    @classmethod
    def get_name(cls):
        return cls.name

