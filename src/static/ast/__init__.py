
from pathlib import Path
import javalang
import sys
from utils import *
import re

from graphviz import Digraph


class Register:
    """
    Class to register Node decorator modules
    """
    funcs = {}
    
    @classmethod
    def add_node(cls, node, state, func):
        if not node in cls.funcs:
            cls.funcs[node] = {"in" : [],
                               "out" : []}
        cls.funcs[node][state].append(func)
    
    @classmethod
    def get_node(cls, node, state):
        if node in cls.funcs:
            return cls.funcs[node][state]
        return []

class Node:
    """
    Decorator Node apply function when th node throwing
    """
    def __init__(self, node, state):
        self.__node = node
        self.__state = state
    def __call__(self, func):
        Register.add_node(self.__node, self.__state, func)
        return func

def protect_node(fun):
    def wrapper_protect_node(*args, **kwargs):
        try:
            func(args, kwargs)
        except:
            sys.stderr.write("an error happend\n")

class ast:
    """
    Class allow to create the AST of the apk
    """
    def __init__(self, tmp_dir, app, args):
        self.__tmp_dir = tmp_dir
        self.__app = app
        self.__infos = {}

        for i in Register.get_node("Init", "in"):
            self.set_infos(i.call(self.get_infos()))

        path_app = '%s/decompiled_app/%s/src' % \
                    (self.__tmp_dir,
                    self.__app.split('/')[-1])
        if args.tree_path:
            path_app += "/" + args.tree_path
        for action in Output.get_store()["manifest"]["activity"]["actions"]:
            if len(action) > 1 and action[1] == "android.intent.action.MAIN":
                self.main = action[0]
        print("/".join(self.main.split(".")))
        for path in Path(path_app).rglob('*.java'):
            #print(path)
            with open(path, 'r') as file:
                try:
                    content = file.read()
                    tree = javalang.parse.parse(content)
                except javalang.parser.JavaSyntaxError:
                    continue
                except javalang.tokenizer.LexerError:
                    continue
                if tree.package == None:
                    continue
                self.__infos["package"] = tree.package.name
                self.l = tree.types

                for i in Register.get_node("File", "in"):
                    self.set_infos(i.call(self.get_infos(), path))

                sys.setrecursionlimit(10**7)

                self.dot = Digraph(comment=self.__infos["package"] + "." +
                        path.name)
                self.dot.attr('node', shape='box')
                self.dot.attr('graph', splines='ortho')

                self.count_node = 0
                self.load()

                #print(self.dot.source)
                try:
                    with timeout(3):
                        self.dot.render('dot/%s.%s' % (self.__infos["package"],
                            path.name), view=False)
                except:
                    pass

        for i in Register.get_node("Init", "out"):
            self.set_infos(i.call(self.get_infos()))

    def set_infos(self, e):
        """Set marker to interact between different nodes"""
        self.__infos = e

    def get_infos(self):
        """Get marker to interact between different nodes"""
        return self.__infos

    def load(self):
        """
        Throwing the AST and apply Nodes modules
        """
        #import pdb; pdb.set_trace()
        for elt in self.l:
            self.elt = elt
            if type(elt) is javalang.tree.ClassDeclaration:
                self.ClassDeclaration(elt).visit(self)
            elif type(elt) is javalang.tree.AnnotationDeclaration:
                self.AnnotationDeclaration(elt).visit(self)
            elif type(elt) is javalang.tree.EnumDeclaration:
                self.EnumDeclaration(elt).visit(self)
            elif type(elt) is javalang.tree.InterfaceDeclaration:
                self.InterfaceDeclaration(elt).visit(self)
            else:
                print(type(elt))

    def hook(self, selfc, state):
        for i in Register.get_node(selfc.__class__.__name__, state):
            self.set_infos(i.call(self.get_infos(), selfc))

    class BaseNode:

        def __init__(self, elt, parent=None):
            self.elt = elt
            self.parent = parent

        def getName(self):
            #print(self.elt)
            return self.__class__.__name__
        
        def NameFormat(self, name):
            return str(self.id) + name.replace(" ", "_").replace(":", "_")

        def visit(self, selfp):
            self.id = selfp.count_node
            if selfp.count_node < 560:
                selfp.count_node = selfp.count_node + 1

            name = self.getName()
            selfp.dot.node(self.NameFormat(name), name)
            if self.parent:
                selfp.dot.edge(self.parent.NameFormat(self.parent.getName()),
                    self.NameFormat(self.getName()), constraint='true')

            selfp.hook(self, "in")
            self.apply(selfp)
            selfp.hook(self, "out")
        
        def apply(self, selfp):
            raise NotImplementedError()
    
    class ClassDeclaration(BaseNode):
        
        def getName(self):
            return self.__class__.__name__ + " : " +self.elt.name

        def apply(self, selfp):
            for elt in self.elt.body:
                if type(elt) is javalang.tree.MethodDeclaration:
                    selfp.MethodDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.FieldDeclaration:
                    selfp.FieldDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ConstructorDeclaration:
                    selfp.ConstructorDeclaration(elt, self).visit(selfp)
                elif type(elt) is list:
                    selfp.ASTList(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ClassDeclaration:
                    selfp.ClassDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.InterfaceDeclaration:
                    selfp.InterfaceDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.EnumDeclaration:
                    selfp.EnumDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.AnnotationDeclaration:
                    selfp.AnnotationDeclaration(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))

 
    class AnnotationDeclaration(BaseNode):
        
        def apply(self, selfp):
            for elt in self.elt.body:
                if type(elt) is javalang.tree.EnumDeclaration:
                    selfp.EnumDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.AnnotationMethod:
                    selfp.AnnotationMethod(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.AnnotationDeclaration:
                    selfp.AnnotationDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ConstantDeclaration:
                    selfp.ConstantDeclaration(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
 
    class EnumDeclaration(BaseNode):

        def apply(self, selfp):
            for elt in self.elt.body:
                if type(elt) is tuple:
                    selfp.ASTList(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')

    class InterfaceDeclaration(BaseNode):

        def apply(self, selfp):
            for elt in self.elt.body:
                if type(elt) is javalang.tree.MethodDeclaration:
                    selfp.MethodDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ClassDeclaration:
                    selfp.ClassDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.InterfaceDeclaration:
                    selfp.InterfaceDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.EnumDeclaration:
                    selfp.EnumDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ConstantDeclaration:
                    selfp.ConstantDeclaration(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
    
    class MethodDeclaration(BaseNode):
        
        def getName(self):
            return self.__class__.__name__ + " : " +self.elt.name

        def apply(self, selfp):
            if self.elt.body == None:
                return # TODO: Fix bug None
            for elt in self.elt.body:
                if type(elt) is javalang.tree.ReturnStatement:
                    selfp.ReturnStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.StatementExpression:
                    selfp.StatementExpression(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.IfStatement:
                    selfp.IfStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.LocalVariableDeclaration:
                    selfp.LocalVariableDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.SynchronizedStatement:
                    selfp.SynchronizedStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.TryStatement:
                    selfp.TryStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ThrowStatement:
                    selfp.ThrowStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.WhileStatement:
                    selfp.WhileStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.BlockStatement:
                    selfp.BlockStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ForStatement:
                    selfp.ForStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.DoStatement:
                    selfp.DoStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.SwitchStatement:
                    selfp.SwitchStatement(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')

    class FieldDeclaration(BaseNode):
        
        def getName(self):
            return self.__class__.__name__

        def apply(self, selfp):
            # No body
            #print(self.elt.__dict__)
            for elt in self.elt.type:
                if type(elt) is tuple:
                    selfp.ASTList(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')

    class ConstructorDeclaration(BaseNode):

        def apply(self, selfp):
            for elt in self.elt.body:
                if type(elt) is javalang.tree.StatementExpression:
                    selfp.StatementExpression(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.IfStatement:
                    selfp.IfStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.LocalVariableDeclaration:
                    selfp.LocalVariableDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ThrowStatement:
                    selfp.ThrowStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.BlockStatement:
                    selfp.BlockStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ForStatement:
                    selfp.ForStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.TryStatement:
                    selfp.TryStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.WhileStatement:
                    selfp.WhileStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.DoStatement:
                    selfp.DoStatement(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))

    class StatementExpression(BaseNode):
        
        def getName(self):
            name = " : " + self.elt.label if self.elt.label else ""
            return self.__class__.__name__ + name

        def apply(self, selfp):
            #print(self.elt.__dict__)
            elt = self.elt.expression
            if type(elt) is javalang.tree.MethodInvocation:
                selfp.MethodInvocation(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.SuperMethodInvocation:
                selfp.SuperMethodInvocation(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.Assignment:
                selfp.Assignment(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.This:
                selfp.This(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.Cast:
                selfp.Cast(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.ClassCreator:
                selfp.ClassCreator(elt, self).visit(selfp)
            else:
                sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))

    class LocalVariableDeclaration(BaseNode):

        def apply(self, selfp):
            #print(self.elt.type.name)
            for elt in self.elt.declarators:
                if type(elt) is javalang.tree.VariableDeclarator:
                    selfp.VariableDeclarator(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')

    class ASTList(BaseNode):

        def getName(self):
            #print(self.elt)
            return self.__class__.__name__

        def apply(self, selfp):
            #print(self.elt)
            #traceback.print_stack()
            for elt in self.elt:
                if type(elt) is javalang.tree.StatementExpression:
                    selfp.StatementExpression(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.LocalVariableDeclaration:
                    selfp.LocalVariableDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.BlockStatement:
                    selfp.BlockStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.IfStatement:
                    selfp.IfStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.TryStatement:
                    selfp.TryStatement(elt, self).visit(selfp)
                #elif type(elt) is tuple:
                #    selfp.ASTList(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.MemberReference:
                    selfp.MemberReference(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.MethodInvocation:
                    selfp.MethodInvocation(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.Assignment:
                    selfp.Assignment(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.Literal:
                    selfp.Literal(elt, self).visit(selfp)
                elif type(elt) is list:
                    selfp.ASTList(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.This:
                    selfp.This(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ClassCreator:
                    selfp.ClassCreator(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.Cast:
                    selfp.Cast(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ReferenceType:
                    selfp.ReferenceType(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ClassReference:
                    selfp.ClassReference(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.SuperMethodInvocation:
                    selfp.SuperMethodInvocation(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.BinaryOperation:
                    selfp.BinaryOperation(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.SuperConstructorInvocation:
                    selfp.SuperConstructorInvocation(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ExplicitConstructorInvocation:
                    selfp.ExplicitConstructorInvocation(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.TypeArgument:
                    selfp.TypeArgument(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ArraySelector:
                    selfp.ArraySelector(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.BasicType:
                    selfp.BasicType(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ArrayInitializer:
                    selfp.ArrayInitializer(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ArrayCreator:
                    selfp.ArrayCreator(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ForStatement:
                    selfp.ForStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ReturnStatement:
                    selfp.ReturnStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.MethodDeclaration:
                    selfp.MethodDeclaration(elt, self).visit(selfp)
                #elif type(elt) is javalang.tree.FieldDeclaration:
                #    selfp.FieldDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.EnumBody:
                    selfp.EnumBody(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ConstructorDeclaration:
                    selfp.ConstructorDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.EnumConstantDeclaration:
                    selfp.EnumConstantDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.VariableDeclarator:
                    selfp.VariableDeclarator(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.FormalParameter:
                    selfp.FormalParameter(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.Annotation:
                    selfp.Annotation(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.TernaryExpression:
                    selfp.TernaryExpression(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ThrowStatement:
                    selfp.ThrowStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.WhileStatement:
                    selfp.WhileStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ContinueStatement:
                    selfp.ContinueStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.BreakStatement:
                    selfp.BreakStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.Statement:
                    selfp.Statement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.SwitchStatement:
                    selfp.SwitchStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.SwitchStatementCase:
                    selfp.SwitchStatementCase(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ForControl:
                    selfp.ForControl(elt, self).visit(selfp)
                #else:
                #    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
    
    #class ASTTuple:

    #    def __init__(self, elt):
    #        self.elt = elt

    #    def visit(self, selfp):
    #        selfp.hook(self, "in")
    #        for elt in self.elt:
    #            print(type(elt))
    #        #print(self.elt.__dict__, end='')
    #        selfp.hook(self, "out")

    class IfStatement(BaseNode):
        
        def getName(self):
            #print(self.elt)
            return self.__class__.__name__

        def apply(self, selfp):
            statements = [self.elt.condition, self.elt.then_statement]
            if self.elt.else_statement:
                statements.append(self.elt.else_statement)
            for elt in statements:
                if type(elt) is javalang.tree.BlockStatement:
                    selfp.BlockStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.StatementExpression:
                    selfp.StatementExpression(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ReturnStatement:
                    selfp.ReturnStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.IfStatement:
                    selfp.IfStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.TryStatement:
                    selfp.TryStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ForStatement:
                    selfp.ForStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.WhileStatement:
                    selfp.WhileStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ContinueStatement:
                    selfp.ContinueStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.BreakStatement:
                    selfp.BreakStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ThrowStatement:
                    selfp.ThrowStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.This:
                    selfp.This(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.MethodInvocation:
                    selfp.MethodInvocation(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')

    class TryStatement(BaseNode):

        def apply(self, selfp):
            self = self
            #for elt in self.elt:
            #    print("%s - %s" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')

    class BlockStatement(BaseNode):

        def apply(self, selfp):
            for elt in self.elt.statements:
                if type(elt) is javalang.tree.StatementExpression:
                    selfp.StatementExpression(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')

    class AnnotationMethod(BaseNode):

        def apply(self, selfp):
            self = self
            #print(self.elt.__dict__, end='')

    class ConstantDeclaration(BaseNode):

        def apply(self, selfp):
            self = self
            #print(self.elt.__dict__, end='')

    class ReturnStatement(BaseNode):

        def apply(self, selfp):
            self = self
            #print(self.elt.__dict__, end='')

    class ThrowStatement(BaseNode):

        def apply(self, selfp):
            self = self
            #print(self.elt.__dict__, end='')

    class SynchronizedStatement(BaseNode):

        def apply(self, selfp):
            self = self
            #print(self.elt.__dict__, end='')

    class ForStatement(BaseNode):

        def apply(self, selfp):
            for elt in self.elt.body:
                if type(elt) is tuple:
                    selfp.ASTList(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')

    class WhileStatement(BaseNode):

        def apply(self, selfp):
            for elt in self.elt.body:
                if type(elt) is tuple:
                    selfp.ASTList(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))

    class SwitchStatement(BaseNode):

        def apply(self, selfp):
            self = self
            #print(self.elt.__dict__, end='')

    class DoStatement(BaseNode):

        def apply(self, selfp):
            self = self
            #print(self.elt.__dict__, end='')

    class MethodInvocation(BaseNode):

        def getName(self):
            qualifier = self.elt.qualifier + "." if self.elt.qualifier else ""
            return self.__class__.__name__ + " : " + qualifier + self.elt.member

        def apply(self, selfp):
            for elt in self.elt.arguments:
                if type(elt) is javalang.tree.MemberReference:
                    selfp.MemberReference(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ClassCreator:
                    selfp.ClassCreator(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.MethodInvocation:
                    selfp.MethodInvocation(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.This:
                    selfp.This(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.Literal:
                    selfp.Literal(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.Cast:
                    selfp.Cast(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ArrayCreator:
                    selfp.ArrayCreator(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.BinaryOperation:
                    selfp.BinaryOperation(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ClassReference:
                    selfp.ClassReference(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')

    class MemberReference(BaseNode):

        def apply(self, selfp):
            self = self

    class Assignment(BaseNode):
        
        #def getName(self):
        #    return self.__class__.__name__ + " : " +self.elt.expressionl.member

        def apply(self, selfp):
            elt = [self.elt.expressionl, self.elt.value]
            for elt in elt:
                if type(elt) is javalang.tree.Cast:
                    selfp.Cast(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ClassCreator:
                    selfp.ClassCreator(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
    
    #final node
    class Literal(BaseNode):
        
        def getName(self):
            return self.__class__.__name__ + " : " +self.elt.value

        def apply(self, selfp):
            pass
    
    class This(BaseNode):

        def apply(self, selfp):
            for elt in self.elt.selectors:
                if type(elt) is javalang.tree.MethodInvocation:
                    selfp.MethodInvocation(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            pass

    class ClassCreator(BaseNode):

        def getName(self):
            return self.__class__.__name__ + " : " +self.elt.type.name

        def apply(self, selfp):
            if self.elt.body == None:
                return # TODO: Fix bug None
            for elt in self.elt.body:
                if type(elt) is javalang.tree.MethodDeclaration:
                    selfp.MethodDeclaration(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))

    class SwitchStatement(BaseNode):

        def apply(self, selfp):
            self = self
            #print(self.elt.__dict__, end='')

    class DoStatement(BaseNode):

        def apply(self, selfp):
            self = self
            #print(self.elt.__dict__, end='')


    class MemberReference(BaseNode):

        def apply(self, selfp):
            self = self

    #final node
    class Literal(BaseNode):
        
        def getName(self):
            return self.__class__.__name__ + " : " +self.elt.value

        def apply(self, selfp):
            pass
    
    class This(BaseNode):

        def apply(self, selfp):
            for elt in self.elt.selectors:
                if type(elt) is javalang.tree.MethodInvocation:
                    selfp.MethodInvocation(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            pass

    class Cast(BaseNode):
        
        def getName(self):
            return self.__class__.__name__ + " : " +self.elt.type.name

        def apply(self, selfp):
            elt = [self.elt.expression]
            if "selectors" in self.elt.__dict__:
                elt.extend(self.elt.selectors)
            for elt in elt:
                if type(elt) is javalang.tree.MethodInvocation:
                    selfp.MethodInvocation(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.SuperMethodInvocation:
                    selfp.SuperMethodInvocation(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.Assignment:
                    selfp.Assignment(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.This:
                    selfp.This(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.Cast:
                    selfp.Cast(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.Literal:
                    selfp.Literal(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.MemberReference:
                    selfp.MemberReference(elt, self).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))

    class ReferenceType(BaseNode):

        def apply(self, selfp):
            pass

    class SuperMethodInvocation(BaseNode):

        def apply(self, selfp):
            pass

    
            pass

    class ClassReference(BaseNode):

        def apply(self, selfp):
            pass

    class SuperConstructorInvocation(BaseNode):

        def apply(self, selfp):
            pass

    class BinaryOperation(BaseNode):

        def apply(self, selfp):
            pass

    class ExplicitConstructorInvocation(BaseNode):

        def apply(self, selfp):
            pass

    class TypeArgument(BaseNode):

        def apply(self, selfp):
            pass

    class BasicType(BaseNode):

        def apply(self, selfp):
            pass

    class ArrayCreator(BaseNode):

        def apply(self, selfp):
            pass

    class ArrayInitializer(BaseNode):

        def apply(self, selfp):
            pass

    class ArraySelector(BaseNode):

        def apply(self, selfp):
            pass

    class EnumBody(BaseNode):

        def apply(self, selfp):
            pass

    class VariableDeclarator(BaseNode):

        def apply(self, selfp):
            if self.elt.initializer == None:
                return
            elt = self.elt.initializer
            if type(elt) is javalang.tree.Cast:
                selfp.Cast(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.MethodInvocation:
                selfp.MethodInvocation(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.ClassCreator:
                selfp.ClassCreator(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.MemberReference:
                selfp.MemberReference(elt, self).visit(selfp)
            else:
                sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')


    class EnumConstantDeclaration(BaseNode):

        def apply(self, selfp):
            pass

    class Annotation(BaseNode):

        def apply(self, selfp):
            pass

    class FormalParameter(BaseNode):

        def apply(self, selfp):
            pass

    class TernaryExpression(BaseNode):

        def apply(self, selfp):
            pass

    class ContinueStatement(BaseNode):

        def apply(self, selfp):
            pass

    class BreakStatement(BaseNode):

        def apply(self, selfp):
            pass

    class Statement(BaseNode):

        def apply(self, selfp):
            pass

    class SwitchStatementCase(BaseNode):

        def apply(self, selfp):
            pass

    class ForControl(BaseNode):

        def apply(self, selfp):
            pass

