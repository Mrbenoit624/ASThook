from asthook.static.ast import Node
from asthook.utils import *
import javalang


def check_print(type_, name):
    checks = ['int', 'java.lang.String']
    for check in checks:
        if (type_.startswith("'[") and type_.endswith("%s'" % check)) or \
                type_ == "'%s'" % check:
            return "%ssend('%s: ' + %s);\n" % (" "*8, name, name)
    else:
        return "%ssend('%s: ' + %s.value);\n" % (" "*8, name, name)


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
                    elif param.type.name == "JSONObject":
                        args.append(("'%sorg.json.JSONObject'" % pretype, "arg%d" % i))
                    elif param.type.name == "int":
                        args.append(("'%sint'" % pretype, "arg%d" % i))
                    else:
                        args.append(("%s<package>.%s" % ( pretype, param.type.name), "arg%d" % i))
                        
                    i = i + 1
            if len([over for over, arg in args if over != ""]) > 0:
                overload += ".overload("
                overload += ",".join([j for j,k in args if j != ""])
                overload += ")"
            #print("%s : %s" % (self.elt.name, params))
            
            #### Return Type ####
            ret_print = ""
            if self.elt.return_type:
                ret_print = "\tsend('ret = ' + ret.value);\n"
            
            for j, k in args:
                prints += check_print(j, k)
            #r["gen_hook_out"].append(\
            Output.add_tree_mod("gen_hook", "hook", ["%s.%s" % (class_name,func_name),
"Java.perform(function()\n\
{\n\
    var class_hook = Java.use('%s.%s')\n\
    //TODO:%s\n\
    class_hook.%s.implementation = function (%s) {\n\
        send('[+] %s.%s hooked');\n\
%s\
        var ret = this.%s(%s);\n\
%s\
        return ret;\n\
    };\n\
});" % (
                r["package"], class_name,
                overload,
                func_name, ",".join(k for j,k in args),
                class_name, func_name,
                prints,
                func_name, ",".join(k for j,k in args),
                ret_print)],
                r["instance"]);
        return r

@Node("ConstructorDeclaration", "in")
class ConstructorDeclarationIn:
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
            construct_init = ""
            for elt in self.parent.elt.body:
                if type(elt) is javalang.tree.FieldDeclaration:
                    construct_init += "%ssend('this.%s: ' + this.%s.value);\n" % (
                            " "*8,
                            elt.declarators[0].name, 
                            elt.declarators[0].name)
            params = ""
            args = []
            overload = ""
            prints = ""
            i=1
            if len(self.elt.parameters) > 0:
                for param in self.elt.parameters:
                    args.append(("", "arg%d" % i))
                    i = i + 1
            for j, k in args:
                prints += "%ssend('%s: ' + %s);\n" % (" "*8,k,k)
            Output.add_tree_mod("gen_hook", "hook", ["%s.%s" % (class_name,func_name),
"Java.perform(function()\n\
{\n\
    var class_hook = Java.use('%s.%s');\n\
    class_hook.$init.implementation = function (%s) {\n\
        send('[+] %s.%s hooked');\n\
%s\
        var ret = this.$init(%s);\n\
        send('ret = ' + ret);\n\
%s\
        return ret\n\
    };\n\
});" % (
                r["package"], class_name,
                ",".join(k for j,k in args),
                class_name, func_name,
                prints,
                ",".join(k for j,k in args),
                construct_init)],
                r["instance"]);
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
    def call(cls, r, self):
        r["gen_hook_out"] = []
        return r

@Node("Init", "out")
class End:
    @classmethod
    def call(cls, r, self):
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

