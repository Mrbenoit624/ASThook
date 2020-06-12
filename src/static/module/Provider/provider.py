from static.ast import Node
from utils import Output
from static.generate_apk import GenerateAPK, JavaFile
import javalang
from logging import debug
from static.module.Taint import taint

from . import mprint

Poc = False
IsProvider = []

@Node("ClassDeclaration", "in")
class ClassDeclarationIn:
    @classmethod
    def call(cls, r, self):
        isprovider = False
        if self.elt.extends and self.elt.extends.name == "ContentProvider":
            isprovider = True
        for auth, prov_name in Output.get_store()["manifest"]["provider"]["exported"]:
            filename = r["Filename"].split("/")[1:]
            prov     = prov_name.split(".")
            if filename[:-1] == prov[:-1]:
                if self.elt.name == prov[-1]:
                    debug(f"File contain provider exported : {r['Filename']}")
                    IsProvider.append(True)
                    return r
        IsProvider.append(False)
        return r

@Node("ClassDeclaration", "out")
class ClassDeclarationOut:
    @classmethod
    def call(cls, r, self):
        IsProvider.pop()
        return r

@Node("MethodInvocation", "in")
class MethodInvocationIn:
    @classmethod
    def call(cls, r, self):
        if IsProvider[-1]:
            if self.elt.member == "match":
                node = taint.TaintElt.get([], self.elt.qualifier)
            if self.elt.member == "addURI":
                val = []
                for argument in self.elt.arguments[:2]:
                    if type(argument) is javalang.tree.Literal:
                        val.append(argument.value)
                    else:
                        node = taint.TaintElt.get([],
                                argument.member).node_get().elt
                        if type(node) is javalang.tree.Assignment:
                            tmp = taint.TaintElt.get([],argument.member).node_get().elt.value
                            #debug(tmp)
                            #debug(taint.revxref(taint.JavaLang2NodeAst(tmp,
                            #    self)))
                            val.append("Not Found")
                        else:
                            val.append(node.declarators[0].initializer.value)
                debug(f"Authorities:{val[0]}, path:{val[1]}")
        return r

@Node("Init", "in")
class Init:
    @classmethod
    def call(cls, r, self):
        return r

