
from pathlib import Path
import javalang

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

class ast:
    """
    Class allow to create the AST of the apk
    """
    def __init__(self, tmp_dir, app):
        self.__tmp_dir = tmp_dir
        self.__app = app
        self.__infos = {}

        for i in Register.get_node("Init", "in"):
            self.set_infos(i.call(self.get_infos()))

        path_app = '%s/decompiled_app/%s' % \
                    (self.__tmp_dir,
                    self.__app.split('/')[-1][:-4].lower())
        for path in Path(path_app).rglob('*.java'):
            #print(path)
            with open(path, 'r') as file:
                try:
                    tree = javalang.parse.parse(file.read())
                except javalang.parser.JavaSyntaxError:
                    continue
                self.l = tree.types

                for i in Register.get_node("File", "in"):
                    self.set_infos(i.call(self.get_infos(), path))

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
            self.__elt = elt
            if type(elt) is javalang.tree.ClassDeclaration:
                self.ClassDeclaration.visit(self)
            elif type(elt) is javalang.tree.AnnotationDeclaration:
                self.AnnotationDeclaration.visit(self)
            elif type(elt) is javalang.tree.EnumDeclaration:
                self.EnumDeclaration.visit(self)
            elif type(elt) is javalang.tree.InterfaceDeclaration:
                self.InterfaceDeclaration.visit(self)
            else:
                print(type(elt))

    class ClassDeclaration:
        
        @classmethod
        def visit(cls, self):
            for i in Register.get_node("ClassDeclaration", "in"):
                self.set_infos(i.call(self.get_infos(), self))
            print("", end='')
 
    class AnnotationDeclaration:
        def __init__(cls):
            print("init")
        
        @classmethod
        def visit(cls, self):
            print("", end='')
 
    class EnumDeclaration:
        def __init__(cls):
            print("init")
        
        @classmethod
        def visit(cls, self):
            print("", end='')

    class InterfaceDeclaration:
        def __init__(cls):
            print("init")
        
        @classmethod
        def visit(cls, self):
            print("", end='')
