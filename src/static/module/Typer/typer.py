from static.ast import Node

import javalang

class EltType:
    def __init__(self, name, type):
        self.name = name
        self.type = type

@Node("MethodDeclaration", "in")
class MethodDeclarationIn:
    @classmethod
    def call(cls, r, self):
        #parameters = []
        #for parameter in self.elt.parameters:
        #    parameters.append((parameter.name, parameter.type.name))
            #print("%s : %s" % (parameter.name,
            #    parameter.type.name), end='\t')
        r["TyperMethod"].append(self.elt.parameters)
        return r

@Node("VariableDeclarator", "in")
class VariableDeclaratorIn:
    @classmethod
    def call(cls, r, self):
        # No Initilizer means unknow type
        if not self.elt.initializer:
            return r
        # Complex type TODO
        if type(self.elt.initializer) is javalang.tree.This or \
                type(self.elt.initializer) is javalang.tree.MemberReference or \
                type(self.elt.initializer) is javalang.tree.MethodInvocation or \
                type(self.elt.initializer) is javalang.tree.BinaryOperation or \
                type(self.elt.initializer) is javalang.tree.Literal or \
                type(self.elt.initializer) is javalang.tree.SuperMethodInvocation or \
                type(self.elt.initializer) is javalang.tree.TernaryExpression:
            return r
        elt = EltType(self.elt.name, self.elt.initializer.type)
        if len(r["TyperMethod"]) == 0:
            r["TyperMethod"].append([elt])
        else:
            r["TyperMethod"][-1].append(elt)
        return r

@Node("MethodDeclaration", "out")
class MethodDeclarationIn:
    @classmethod
    def call(cls, r, self):
        r["TyperMethod"].pop()
        return r

@Node("File", "in")
class File:
    @classmethod
    def call(cls, r, path):
        r["TyperMethod"] = []
        return r
#
#@Node("Init", "in")
#class Init:
#    @classmethod
#    def call(cls, r):
#        return r
