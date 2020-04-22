
from pathlib import Path
import javalang
import sys

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
        for path in Path(path_app).rglob('*.java'):
            #print(path)
            with open(path, 'r') as file:
                try:
                    tree = javalang.parse.parse(file.read())
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

                self.load()

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


    class ClassDeclaration:
        
        def __init__(self, elt):
            self.elt = elt
        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            for elt in self.elt.body:
                if type(elt) is javalang.tree.MethodDeclaration:
                    selfp.MethodDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.FieldDeclaration:
                    selfp.FieldDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.ConstructorDeclaration:
                    selfp.ConstructorDeclaration(elt).visit(selfp)
                elif type(elt) is list:
                    selfp.ASTList(elt).visit(selfp)
                elif type(elt) is javalang.tree.ClassDeclaration:
                    selfp.ClassDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.InterfaceDeclaration:
                    selfp.InterfaceDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.EnumDeclaration:
                    selfp.EnumDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.AnnotationDeclaration:
                    selfp.AnnotationDeclaration(elt).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            selfp.hook(self, "out")
 
    class AnnotationDeclaration:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            for elt in self.elt.body:
                if type(elt) is javalang.tree.EnumDeclaration:
                    selfp.EnumDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.AnnotationMethod:
                    selfp.AnnotationMethod(elt).visit(selfp)
                elif type(elt) is javalang.tree.AnnotationDeclaration:
                    selfp.AnnotationDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.ConstantDeclaration:
                    selfp.ConstantDeclaration(elt).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")
 
    class EnumDeclaration:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            for elt in self.elt.body:
                if type(elt) is tuple:
                    selfp.ASTList(elt).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class InterfaceDeclaration:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            for elt in self.elt.body:
                if type(elt) is javalang.tree.MethodDeclaration:
                    selfp.MethodDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.ClassDeclaration:
                    selfp.ClassDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.InterfaceDeclaration:
                    selfp.InterfaceDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.EnumDeclaration:
                    selfp.EnumDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.ConstantDeclaration:
                    selfp.ConstantDeclaration(elt).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")
    
    class MethodDeclaration:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            if self.elt.body == None:
                return # TODO: Fix bug None
            for elt in self.elt.body:
                if type(elt) is javalang.tree.ReturnStatement:
                    selfp.ReturnStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.StatementExpression:
                    selfp.StatementExpression(elt).visit(selfp)
                elif type(elt) is javalang.tree.IfStatement:
                    selfp.IfStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.LocalVariableDeclaration:
                    selfp.LocalVariableDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.SynchronizedStatement:
                    selfp.SynchronizedStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.TryStatement:
                    selfp.TryStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.ThrowStatement:
                    selfp.ThrowStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.WhileStatement:
                    selfp.WhileStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.BlockStatement:
                    selfp.BlockStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.ForStatement:
                    selfp.ForStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.DoStatement:
                    selfp.DoStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.SwitchStatement:
                    selfp.SwitchStatement(elt).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class FieldDeclaration:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            # No body
            selfp.hook(self, "in")
            #print(self.elt.__dict__)
            for elt in self.elt.type:
                if type(elt) is tuple:
                    selfp.ASTList(elt).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class ConstructorDeclaration:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            for elt in self.elt.body:
                if type(elt) is javalang.tree.StatementExpression:
                    selfp.StatementExpression(elt).visit(selfp)
                elif type(elt) is javalang.tree.IfStatement:
                    selfp.IfStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.LocalVariableDeclaration:
                    selfp.LocalVariableDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.ThrowStatement:
                    selfp.ThrowStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.BlockStatement:
                    selfp.BlockStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.ForStatement:
                    selfp.ForStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.TryStatement:
                    selfp.TryStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.WhileStatement:
                    selfp.WhileStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.DoStatement:
                    selfp.DoStatement(elt).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            selfp.hook(self, "out")

    class StatementExpression:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__)
            for elt in self.elt.expression:
                if type(elt) is tuple:
                    selfp.ASTList(elt).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            selfp.hook(self, "out")

    class LocalVariableDeclaration:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.type.name)
            #for elt in self.elt.body:
            #    print("%s - %s" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class ASTList:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            for elt in self.elt:
                if type(elt) is javalang.tree.StatementExpression:
                    selfp.StatementExpression(elt).visit(selfp)
                elif type(elt) is javalang.tree.LocalVariableDeclaration:
                    selfp.LocalVariableDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.BlockStatement:
                    selfp.BlockStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.IfStatement:
                    selfp.IfStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.TryStatement:
                    selfp.TryStatement(elt).visit(selfp)
                elif type(elt) is tuple:
                    selfp.ASTList(elt).visit(selfp)
                elif type(elt) is javalang.tree.MemberReference:
                    selfp.MemberReference(elt).visit(selfp)
                elif type(elt) is javalang.tree.MethodInvocation:
                    selfp.MethodInvocation(elt).visit(selfp)
                elif type(elt) is javalang.tree.Assignment:
                    selfp.Assignment(elt).visit(selfp)
                elif type(elt) is javalang.tree.Literal:
                    selfp.Literal(elt).visit(selfp)
                elif type(elt) is list:
                    selfp.ASTList(elt).visit(selfp)
                elif type(elt) is javalang.tree.This:
                    selfp.This(elt).visit(selfp)
                elif type(elt) is javalang.tree.ClassCreator:
                    selfp.ClassCreator(elt).visit(selfp)
                elif type(elt) is javalang.tree.Cast:
                    selfp.Cast(elt).visit(selfp)
                elif type(elt) is javalang.tree.ReferenceType:
                    selfp.ReferenceType(elt).visit(selfp)
                elif type(elt) is javalang.tree.ClassReference:
                    selfp.ClassReference(elt).visit(selfp)
                elif type(elt) is javalang.tree.SuperMethodInvocation:
                    selfp.SuperMethodInvocation(elt).visit(selfp)
                elif type(elt) is javalang.tree.BinaryOperation:
                    selfp.BinaryOperation(elt).visit(selfp)
                elif type(elt) is javalang.tree.SuperConstructorInvocation:
                    selfp.SuperConstructorInvocation(elt).visit(selfp)
                elif type(elt) is javalang.tree.ExplicitConstructorInvocation:
                    selfp.ExplicitConstructorInvocation(elt).visit(selfp)
                elif type(elt) is javalang.tree.TypeArgument:
                    selfp.TypeArgument(elt).visit(selfp)
                elif type(elt) is javalang.tree.ArraySelector:
                    selfp.ArraySelector(elt).visit(selfp)
                elif type(elt) is javalang.tree.BasicType:
                    selfp.BasicType(elt).visit(selfp)
                elif type(elt) is javalang.tree.ArrayInitializer:
                    selfp.ArrayInitializer(elt).visit(selfp)
                elif type(elt) is javalang.tree.ArrayCreator:
                    selfp.ArrayCreator(elt).visit(selfp)
                elif type(elt) is javalang.tree.ForStatement:
                    selfp.ForStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.ReturnStatement:
                    selfp.ReturnStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.MethodDeclaration:
                    selfp.MethodDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.FieldDeclaration:
                    selfp.FieldDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.EnumBody:
                    selfp.EnumBody(elt).visit(selfp)
                elif type(elt) is javalang.tree.ConstructorDeclaration:
                    selfp.ConstructorDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.EnumConstantDeclaration:
                    selfp.EnumConstantDeclaration(elt).visit(selfp)
                elif type(elt) is javalang.tree.VariableDeclarator:
                    selfp.VariableDeclarator(elt).visit(selfp)
                elif type(elt) is javalang.tree.FormalParameter:
                    selfp.FormalParameter(elt).visit(selfp)
                elif type(elt) is javalang.tree.Annotation:
                    selfp.Annotation(elt).visit(selfp)
                elif type(elt) is javalang.tree.TernaryExpression:
                    selfp.TernaryExpression(elt).visit(selfp)
                elif type(elt) is javalang.tree.ThrowStatement:
                    selfp.ThrowStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.WhileStatement:
                    selfp.WhileStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.ContinueStatement:
                    selfp.ContinueStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.BreakStatement:
                    selfp.BreakStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.Statement:
                    selfp.Statement(elt).visit(selfp)
                elif type(elt) is javalang.tree.SwitchStatement:
                    selfp.SwitchStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.SwitchStatementCase:
                    selfp.SwitchStatementCase(elt).visit(selfp)
                elif type(elt) is javalang.tree.ForControl:
                    selfp.ForControl(elt).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")
    
    #class ASTTuple:

    #    def __init__(self, elt):
    #        self.elt = elt

    #    def visit(self, selfp):
    #        selfp.hook(self, "in")
    #        for elt in self.elt:
    #            print(type(elt))
    #        #print(self.elt.__dict__, end='')
    #        selfp.hook(self, "out")

    class IfStatement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            statements = [self.elt.then_statement]
            if self.elt.else_statement:
                statements.append(self.elt.else_statement)
            for elt in statements:
                if type(elt) is javalang.tree.BlockStatement:
                    selfp.BlockStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.StatementExpression:
                    selfp.StatementExpression(elt).visit(selfp)
                elif type(elt) is javalang.tree.ReturnStatement:
                    selfp.ReturnStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.IfStatement:
                    selfp.IfStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.TryStatement:
                    selfp.TryStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.ForStatement:
                    selfp.ForStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.WhileStatement:
                    selfp.WhileStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.ContinueStatement:
                    selfp.ContinueStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.BreakStatement:
                    selfp.BreakStatement(elt).visit(selfp)
                elif type(elt) is javalang.tree.ThrowStatement:
                    selfp.ThrowStatement(elt).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class TryStatement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #for elt in self.elt:
            #    print("%s - %s" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class BlockStatement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class AnnotationMethod:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class ConstantDeclaration:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class ReturnStatement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class ThrowStatement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class SynchronizedStatement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class ForStatement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            for elt in self.elt.body:
                if type(elt) is tuple:
                    selfp.ASTList(elt).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class WhileStatement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            for elt in self.elt.body:
                if type(elt) is tuple:
                    selfp.ASTList(elt).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class SwitchStatement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class DoStatement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class MethodInvocation:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            for elt in self.elt.arguments:
                if type(elt) is javalang.tree.MemberReference:
                    selfp.MemberReference(elt).visit(selfp)
                elif type(elt) is javalang.tree.ClassCreator:
                    selfp.ClassCreator(elt).visit(selfp)
                elif type(elt) is javalang.tree.MethodInvocation:
                    selfp.MethodInvocation(elt).visit(selfp)
                elif type(elt) is javalang.tree.This:
                    selfp.This(elt).visit(selfp)
                elif type(elt) is javalang.tree.Literal:
                    selfp.Literal(elt).visit(selfp)
                elif type(elt) is javalang.tree.Cast:
                    selfp.Cast(elt).visit(selfp)
                elif type(elt) is javalang.tree.ArrayCreator:
                    selfp.ArrayCreator(elt).visit(selfp)
                elif type(elt) is javalang.tree.BinaryOperation:
                    selfp.BinaryOperation(elt).visit(selfp)
                elif type(elt) is javalang.tree.ClassReference:
                    selfp.ClassReference(elt).visit(selfp)
                else:
                    sys.stderr.write("%s - %s\n" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class MemberReference:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class Assignment:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class Literal:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")
    
    class This:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class ClassCreator:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class Cast:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class ReferenceType:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class SuperMethodInvocation:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class ClassReference:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class SuperConstructorInvocation:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class BinaryOperation:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class ExplicitConstructorInvocation:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class TypeArgument:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class BasicType:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class ArrayCreator:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class ArrayInitializer:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class ArraySelector:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class EnumBody:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class VariableDeclarator:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")


    class EnumConstantDeclaration:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class Annotation:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")


    class FormalParameter:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")


    class TernaryExpression:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")


    class ContinueStatement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class BreakStatement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")


    class Statement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class SwitchStatementCase:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class ForControl:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

