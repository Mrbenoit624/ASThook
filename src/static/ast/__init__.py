
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
            print("an error happend")

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
                #while len(l) > 0:
                #    elt = l.pop()
                #    #print(type(elt))#.name)#__dict__)
                #    if type(elt) is javalang.tree.ClassDeclaration:
                #        print("Class %s" % elt.name)
                #    elif type(elt) is javalang.tree.MethodDeclaration:
                #        print("Method %s" % elt.name)
                #    elif type(elt) is javalang.tree.StatementExpression:
                #        if type(elt.expression) is javalang.tree.Assignment:
                #            continue
                #        if type(elt.expression) is javalang.tree.This:
                #            continue
                #        if type(elt.expression) is javalang.tree.SuperConstructorInvocation:
                #            continue
                #        if type(elt.expression) is javalang.tree.ExplicitConstructorInvocation:
                #            continue
                #        if type(elt.expression) is javalang.tree.ClassCreator:
                #            continue
                #        if type(elt.expression) is javalang.tree.Cast:
                #            continue
                #        print("FunctionCall %s" % elt.expression.member)
                #        continue
                #    elif type(elt) is javalang.tree.LocalVariableDeclaration:
                #        for i in elt.declarators:
                #            l.append(i)
                #        #print(elt.__dict__)
                #        continue
                #    elif type(elt) is javalang.tree.VariableDeclarator:
                #        print("Variable %s" % elt.name)
                #        continue
                #    elif type(elt) is javalang.tree.AnnotationMethod:
                #        continue
                #    elif type(elt) is javalang.tree.ConstantDeclaration:
                #        continue
                #    elif type(elt) is javalang.tree.FieldDeclaration:
                #        continue
                #    elif type(elt) is javalang.tree.ReturnStatement:
                #        continue
                #    elif type(elt) is javalang.tree.TryStatement:
                #        continue
                #    elif type(elt) is javalang.tree.Assignment:
                #        continue
                #    elif type(elt) is javalang.tree.IfStatement:
                #        continue
                #    elif type(elt) is javalang.tree.SynchronizedStatement:
                #        continue
                #    elif type(elt) is javalang.tree.ThrowStatement:
                #        continue
                #    elif type(elt) is javalang.tree.BlockStatement:
                #        continue
                #    elif type(elt) is javalang.tree.SwitchStatement:
                #        continue
                #    elif type(elt) is list:
                #        for i in elt:
                #            l.append(i)
                #        continue
                #    elif type(elt) is tuple:
                #        continue
                #    if elt.body is None:
                #        continue
                #    #print("Name %s" % elt.name)
                #    for i in elt.body:
                #        l.append(i)
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
                    print("%s - %s" % (self.__class__.__name__, type(elt)))
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
                else:
                    print("%s - %s" % (self.__class__.__name__, type(elt)))
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
                    print("%s - %s" % (self.__class__.__name__, type(elt)))
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
                    print("%s - %s" % (self.__class__.__name__, type(elt)))
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
                    print("%s - %s" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class FieldDeclaration:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            # No body
            selfp.hook(self, "in")
            #print(self.elt.__dict__)
            #for elt in self.elt.body:
            #    print("%s - %s" % (self.__class__.__name__, type(elt)))
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
                    print("%s - %s" % (self.__class__.__name__, type(elt)))
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
                    print("%s - %s" % (self.__class__.__name__, type(elt)))
            selfp.hook(self, "out")

    class LocalVariableDeclaration:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
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
                #else:
                #    print("%s - %s" % (self.__class__.__name__, type(elt)))
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
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class TryStatement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
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
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class WhileStatement:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
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
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

    class MemberReference:

        def __init__(self, elt):
            self.elt = elt

        def visit(self, selfp):
            selfp.hook(self, "in")
            #print(self.elt.__dict__, end='')
            selfp.hook(self, "out")

