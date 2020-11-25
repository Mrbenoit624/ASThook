
from pathlib import Path
import javalang
import sys
from asthook.utils import *
import re

from .AstInRam import AstInRam

import asthook.log as logging


from graphviz import Digraph

import pickle


class Register:
    """
    Class to register Node decorator modules
    """
    funcs = [{}]
    instance = 0

    @classmethod
    def set_instance(cls, instance):
        cls.instance = instance
    
    @classmethod
    def add_node(cls, node, state, func):
        if len(cls.funcs) <= cls.instance:
            cls.funcs.append({})
        if not node in cls.funcs[cls.instance]:
            cls.funcs[cls.instance][node] = {"in"      : [],
                               "post-in" : [],
                               "out"     : []}
        cls.funcs[cls.instance][node][state].append(func)
    
    @classmethod
    def get_node(cls, node, state, instance=0):
        if len(cls.funcs) <= cls.instance:
            cls.funcs.append({})
        if node in cls.funcs[instance]:
            return cls.funcs[instance][node][state]
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
            logging.error("an error happend")

class ast:
    """
    Class allow to create the AST of the apk
    """

    class DepNode:

        def __init__(self, base_path, hascache):
            self.hasparent = 0
            self.childs = []
            self.content = None
            self.path = None
            self.hascache = hascache
            self.cache_path = Path(f"{base_path}/decompiled_app/cache/")

        def __str__(self):
            ret = str(self.path)
            if len(self.childs) > 0:
                ret += " -> " + ",".join(str(c) for c in self.childs)
            return ret

        def parse(self, path):
            if self.content:
                return self.content.imports
            if not self.cache_path.is_dir():
                self.cache_path.mkdir(parents=True)
            self.path = path

            package_name = ".".join(str(path).split("/"))
            path_pck = Path(f"{self.cache_path}/{package_name}")
            if path_pck.is_file() and self.hascache:
                with open(f"{self.cache_path}/{package_name}", 'rb') as bak:
                    self.content = pickle.load(bak)
                if self.content:
                    return self.content.imports
                return []



            with open(path, 'r') as file:
                code_valid = False
                correct = ""
                content = file.read()
                tree = None
                while True:
                    try:
                        tree = javalang.parse.parse(content)
                        code_valid = True
                        break
                    except javalang.parser.JavaSyntaxError as err:
                        if correct == "":
                            logging.error("%s on %s at %s" % (err.description, path, err.at))
                        if not err.at.position:
                            break
                        correct = content.split('\n')
                        correct[err.at.position.line - 1] = "//" + correct[err.at.position.line -1]
                        content = "\n".join(correct)
                        continue
                    except javalang.tokenizer.LexerError:
                        break
                with open(f"{self.cache_path}/{package_name}", 'wb') as bak:
                    pickle.dump(tree, bak, pickle.HIGHEST_PROTOCOL)
                if not code_valid:
                    return []
                if tree.package == None:
                    return []
                self.content = tree
                return tree.imports



    def get_tmp(self):
        return self.__basepath

    def __init__(self, base_path, app, args, instance=0, conn=None):
        self.__basepath = base_path
        self.__app = app
        self.__infos = {'instance': instance}
        self.args = args
        self.instance = instance


        for i in Register.get_node("Init", "in", self.instance):
            self.set_infos(i.call(self.get_infos(), self))

        path_app_base = '%s/%s/src' % \
                    (self.__basepath,
                     "decompiled_app")
        #for action in Output.get_store(instance)["manifest"]["activity"]["action"]:
        #    if action['action'] == "android.intent.action.MAIN":
        #        self.main = action['action']
        #        print(action['action'])
        #
        #print("/".join(self.main.split(".")))
        paths = []
        if args.tree_path:
            npaths = []
            for tree_path in args.tree_path:
                path_app = path_app_base
                path_app += "/" + tree_path
                paths_pre = path_app.split('/')
                npaths = list(Path("/".join(paths_pre[:-1])).rglob(f'{paths_pre[-1]}*.java'))
                paths = list(set().union(npaths, paths))
        else:
            paths = list(Path(path_app_base).rglob('*.java'))
        
        if args.tree_exclude:
            for ex_path in args.tree_exclude:
                npath = []
                for pi in paths:
                    if not str(pi).startswith(str(Path(path_app_base + ex_path))):
                        npath.append(pi)
                paths = npath

        percent_max = len(paths)
        path_circle = []

        depnodes = {}
        for p in paths:
            if args.progress:
                percent = int((paths.index(p))/percent_max * 50)
                if conn:
                    conn.send("progress")
                    conn.send(percent)
                else:
                    print(f"\r{percent}%", end='')
            if p in depnodes:
                depnode = depnodes[p]
            elif not AstInRam.askpath(args.app, p) == None:
                depnode = AstInRam.askpath(args.app, p)
                depnodes[p] = depnode
            else:
                depnode = self.DepNode(self.__basepath, not args.no_cache)
                depnodes[p] = depnode
                AstInRam.addpath(args.app, p, depnode)
            imports = depnode.parse(p)
            for i in imports:
                path_import = Path('%s/%s/src/%s%s' % \
                                  (self.__basepath,
                                   "decompiled_app",
                                   "/".join(i.path.split('.')),
                                   ".java"))
                if path_import in paths:
                    if path_import in depnodes:
                        depnode_ch = depnodes[path_import]
                    else:
                        depnode_ch = self.DepNode(self.__basepath,
                                not args.no_cache)
                        depnodes[path_import] = depnode_ch
                    depnode_ch.hasparent += 1
                    depnode.childs.append(depnode_ch)

        while len(depnodes) > 0:
            to_remove = []
            for k, v in depnodes.items():
                if v.hasparent == 0:
                    #print(v)
                    for ch in v.childs:
                        ch.hasparent -= 1
                    to_remove.append(k)
            if len(to_remove) == 0:
                to_remove.append(next(iter(depnodes)))
            for path in to_remove:
                tree = depnodes[path].content
                del depnodes[path]
                if not tree or not tree.package:
                    continue

                #print(path)
                self.__infos["package"] = tree.package.name
                self.__infos["imports"] = tree.imports
                self.l = tree.types

                if args.progress:
                    percent = 50 + int((percent_max - len(depnodes))/percent_max * 50)
                    if conn:
                        conn.send("progress")
                        conn.send(percent)
                    else:
                        print(f"\r{percent}%", end='')
                for i in Register.get_node("File", "in", self.instance):
                    self.set_infos(i.call(self.get_infos(), path))

                sys.setrecursionlimit(10**7)

                if args.graph_ast:
                    self.init_graph(path)

                self.load()

                #print(self.dot.source)
                try:
                    with timeout(3):
                        self.dot.render('dot/%s.%s' % (self.__infos["package"],
                            path.name), view=False)
                except:
                    pass
        for i in Register.get_node("Init", "out", self.instance):
            self.set_infos(i.call(self.get_infos(), self))



    def init_graph(self, path):
        self.dot = Digraph(comment=self.__infos["package"] + "." +
                path.name)
        self.dot.attr('node', shape='box')
        self.dot.attr('graph', splines='ortho')
        self.count_node = 0

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
        for i in Register.get_node(selfc.__class__.__name__, state,
                self.instance):
            r = i.call(self.get_infos(), selfc)
            assert r != None # return miss in one of this module
            self.set_infos(r)

    class BaseNode:

        class NodeGraph:

            def __init__(self):
                self.Name = ""
                self.Shape = "box"
                self.Style = ""
                self.FillColor = ""
                self.Color = ""

        def __init__(self, elt, parent=None):
            self.elt = elt
            self.parent = parent

        def getName(self):
            #print(self.elt)
            return self.__class__.__name__

        def getEgdeLabel(self):
            return ""
        
        def NameFormat(self, name):
            return str(self.id) + name.replace(" ", "_").replace(":", "_")

        def graph(self, selfp):
            self.id = selfp.count_node
            selfp.count_node +=1

            if "active_graph" in selfp.get_infos() and \
                    not selfp.get_infos()["active_graph"]:
                return

            name = self.getName()
            if self.node_graph.Name == "":
                self.node_graph.Name = name
            selfp.dot.node(self.NameFormat(name), self.node_graph.Name,
                    style=self.node_graph.Style,
                    fillcolor=self.node_graph.FillColor,
                    color=self.node_graph.Color,
                    shape=self.node_graph.Shape)
            
            parent = self.parent
            while True:
                if not parent:
                    break
                if any(parent.NameFormat(parent.getName()) in s for s in selfp.dot.body):
                    selfp.dot.edge(parent.NameFormat(parent.getName()),
                            self.NameFormat(self.getName()),
                            label=self.getEgdeLabel(),
                            constraint='true')
                    break
                else:
                    parent = parent.parent

        def visit(self, selfp):

            # if selfp.args.graph: # TODO : thinks what is the best opti vs
            # friendly
            self.node_graph = self.NodeGraph()

            selfp.hook(self, "in")
            
            if selfp.args.graph_ast:
                self.graph(selfp)
            
            selfp.hook(self, "post-in")
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
                elif type(elt) is list: # list of declaration variable
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
                    if selfp.args.debug_ast:
                        logging.error("%s - %s" % (self.__class__.__name__, type(elt)))

 
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
                    if selfp.args.debug_ast:
                        logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
 
    class EnumDeclaration(BaseNode):

        def apply(self, selfp):
            for elt in self.elt.body:
                #if type(elt) is tuple:
                #    selfp.ASTList(elt, self).visit(selfp)
                #else:
                if selfp.args.debug_ast:
                    logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
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
                    if selfp.args.debug_ast:
                        logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
    
    class MethodDeclaration(BaseNode):
        
        def getName(self):
            return self.__class__.__name__ + " : " +self.elt.name

        def apply(self, selfp):
            if self.elt.body == None:
                return # TODO: Fix bug None
            for elt in self.elt.parameters:
                selfp.MethodDeclarationParameters(elt, self).visit(selfp)
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
                    if selfp.args.debug_ast:
                        logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')

    class MethodDeclarationParameters(BaseNode):

        def apply(self, selfp):
            #print(self.elt)
            pass


    class FieldDeclaration(BaseNode):
        
        # TODO print multi fields
        def getName(self):
            return self.__class__.__name__ + " : " + self.elt.declarators[0].name

        def apply(self, selfp):
            for elt in self.elt.declarators:
                if type(elt) is javalang.tree.VariableDeclarator:
                    selfp.VariableDeclarator(elt, self).visit(selfp)
                else:
                    if selfp.args.debug_ast:
                        logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
            pass
            # No body
            #print(self.elt.__dict__)
            #print(self.elt.__dict__, end='')

    class ConstructorDeclaration(BaseNode):

        def getName(self):
            return self.__class__.__name__ + " : " + self.elt.name

        def apply(self, selfp):
            for elt in self.elt.parameters:
                selfp.ConstructorDeclarationParameters(elt, self).visit(selfp)
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
                    if selfp.args.debug_ast:
                        logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
    
    class ConstructorDeclarationParameters(BaseNode):

        def apply(self, selfp):
            pass

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
            elif type(elt) is javalang.tree.SuperConstructorInvocation:
                selfp.SuperConstructorInvocation(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.ExplicitConstructorInvocation:
                selfp.ExplicitConstructorInvocation(elt, self).visit(selfp)
            else:
                if selfp.args.debug_ast:
                    logging.error("%s - %s" % (self.__class__.__name__, type(elt)))

    class LocalVariableDeclaration(BaseNode):

        def getName(self):
            #print(self.elt)
            return self.__class__.__name__ + " : " + self.elt.type.name

        def apply(self, selfp):
            #print(self.elt.type.name)
            #print(self.elt.declarators[0].name)
            for elt in self.elt.declarators:
                if type(elt) is javalang.tree.VariableDeclarator:
                    selfp.VariableDeclarator(elt, self).visit(selfp)
                else:
                    if selfp.args.debug_ast:
                        logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
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
            selfp.IfStatementCondition(self.elt.condition, self).visit(selfp)
            statements = [ self.elt.then_statement]
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
                    if selfp.args.debug_ast:
                        logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
    
    class IfStatementCondition(BaseNode):

        def apply(self, selfp):
            elt = self.elt
            if type(elt) is javalang.tree.MethodInvocation:
                selfp.MethodInvocation(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.BinaryOperation:
                selfp.BinaryOperation(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.This:
                selfp.This(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.MemberReference:
                selfp.MemberReference(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.Literal:
                selfp.Literal(elt, self).visit(selfp)
            else:
                if selfp.args.debug_ast:
                    logging.error("%s - %s" % (self.__class__.__name__, type(elt)))

    class TryStatement(BaseNode):

        def apply(self, selfp):
            for elt in self.elt.block:
                selfp.TryStatementBlock(elt, self).visit(selfp)
            if self.elt.catches:
                for elt in self.elt.catches:
                    selfp.CatchClause(elt, self).visit(selfp)
            if self.elt.finally_block:
                for elt in self.elt.finally_block:
                    selfp.TryStatementFinally(elt, self).visit(selfp)
            #for elt in self.elt:
            #    print("%s - %s" % (self.__class__.__name__, type(elt)))
            #print(self.elt.__dict__, end='')
    
    class TryStatementFinally(BaseNode):
        
        def apply(self, selfp):
            elt = self.elt
            if type(elt) is javalang.tree.LocalVariableDeclaration:
                selfp.LocalVariableDeclaration(elt, self).visit(selfp)
            elif selfp.args.debug_ast:
                logging.error("%s - %s" % (self.__class__.__name__, type(elt)))

    class TryStatementBlock(BaseNode):
        
        def apply(self, selfp):
            elt = self.elt
            if type(elt) is javalang.tree.LocalVariableDeclaration:
                selfp.LocalVariableDeclaration(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.StatementExpression:
                selfp.StatementExpression(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.TryStatement:
                selfp.TryStatement(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.WhileStatement:
                selfp.WhileStatement(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.ReturnStatement:
                selfp.ReturnStatement(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.IfStatement:
                selfp.IfStatement(elt, self).visit(selfp)
            else:
                if selfp.args.debug_ast:
                    logging.error("%s - %s" % (self.__class__.__name__, type(elt)))

    class CatchClause(BaseNode):

        def apply(self, selfp):
            for elt in self.elt.block:
                if type(elt) is javalang.tree.StatementExpression:
                    selfp.StatementExpression(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ThrowStatement:
                    selfp.ThrowStatement(elt, self).visit(selfp)
                elif selfp.args.debug_ast:
                    logging.error("%s - %s" % (self.__class__.__name__, type(elt)))

    class BlockStatement(BaseNode):

        def apply(self, selfp):
            for elt in self.elt.statements:
                if type(elt) is javalang.tree.StatementExpression:
                    selfp.StatementExpression(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.LocalVariableDeclaration:
                    selfp.LocalVariableDeclaration(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ForStatement:
                    selfp.ForStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.IfStatement:
                    selfp.IfStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ReturnStatement:
                    selfp.ReturnStatement(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.TryStatement:
                    selfp.TryStatement(elt, self).visit(selfp)
                else:
                    if selfp.args.debug_ast:
                        logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
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
            elt = self.elt.expression
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
            elif type(elt) is javalang.tree.MethodDeclaration:
                selfp.MethodDeclaration(elt, self).visit(selfp)
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
            else:
                if selfp.args.debug_ast:
                    logging.error("%s - %s" % (self.__class__.__name__, type(elt)))

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
            elt = self.elt.body
            if type(elt) is javalang.tree.BlockStatement:
                selfp.BlockStatement(elt, self).visit(selfp)
            else:
                if selfp.args.debug_ast:
                    logging.error("%s - %s" % (self.__class__.__name__, type(elt)))

    class WhileStatement(BaseNode):

        def apply(self, selfp):
            selfp.WhileStatementCondition(self.elt.condition, self).visit(selfp)
            elt = self.elt.body
            if type(elt) is javalang.tree.BlockStatement:
                selfp.BlockStatement(elt, self).visit(selfp)
            else:
                if selfp.args.debug_ast:
                    logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
    
    class WhileStatementCondition(BaseNode):
        
        def apply(self, selfp):
            elt = self.elt
            if type(elt) is javalang.tree.MethodInvocation:
                selfp.MethodInvocation(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.BinaryOperation:
                selfp.BinaryOperation(elt, self).visit(selfp)
            else:
                if selfp.args.debug_ast:
                    logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
            pass

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
            #logging.debug(self.elt)
            if self.elt.selectors:
                for elt in self.elt.selectors:
                    if type(elt) is javalang.tree.MethodInvocation:
                        selfp.MethodInvocation(elt, self).visit(selfp)
                    elif type(elt) is javalang.tree.MemberReference:
                        selfp.MemberReference(elt, self).visit(selfp)
                    else:
                        if selfp.args.debug_ast:
                            logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
            for elt in self.elt.arguments:
                selfp.MethodInvocationParameters(elt, self).visit(selfp)
            #print(self.elt.__dict__, end='')
    
    class MethodInvocationParameters(BaseNode):
        def apply(self, selfp):
            elt = self.elt
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
                if selfp.args.debug_ast:
                    logging.error("%s - %s" % (self.__class__.__name__, type(elt)))


    class Assignment(BaseNode):
        
        #def getName(self):
        #    return self.__class__.__name__ + " : " +self.elt.expressionl.member

        def apply(self, selfp):
            selfp.AssignmentVar(self.elt.expressionl, self).visit(selfp)
            selfp.AssignmentValue(self.elt.value, self).visit(selfp)
    
    class AssignmentVar(BaseNode):
 
        def apply(self, selfp):
            elt = self.elt
            if type(elt) is javalang.tree.Cast:
                selfp.Cast(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.ClassCreator:
                selfp.ClassCreator(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.MemberReference:
                selfp.MemberReference(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.Literal:
                selfp.Literal(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.This:
                selfp.This(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.MethodInvocation:
                selfp.MethodInvocation(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.Assignment:
                selfp.Assignment(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.BinaryOperation:
                selfp.BinaryOperation(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.ArrayCreator:
                selfp.ArrayCreator(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.TernaryExpression:
                selfp.TernaryExpression(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.ClassReference:
                selfp.ClassReference(elt, self).visit(selfp)
            else:
                if selfp.args.debug_ast:
                    logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
 
    class AssignmentValue(BaseNode):
 
        def apply(self, selfp):
            elt = self.elt
            if type(elt) is javalang.tree.Cast:
                selfp.Cast(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.ClassCreator:
                selfp.ClassCreator(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.MemberReference:
                selfp.MemberReference(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.Literal:
                selfp.Literal(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.This:
                selfp.This(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.MethodInvocation:
                selfp.MethodInvocation(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.Assignment:
                selfp.Assignment(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.BinaryOperation:
                selfp.BinaryOperation(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.ArrayCreator:
                selfp.ArrayCreator(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.TernaryExpression:
                selfp.TernaryExpression(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.ClassReference:
                selfp.ClassReference(elt, self).visit(selfp)
            else:
                if selfp.args.debug_ast:
                    logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
    
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
                elif type(elt) is javalang.tree.MemberReference:
                    selfp.MemberReference(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.ArraySelector:
                    selfp.ArraySelector(elt, self).visit(selfp)
                else:
                    if selfp.args.debug_ast:
                        logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
            pass

    class ClassCreator(BaseNode):

        def getName(self):
            return self.__class__.__name__ + " : " +self.elt.type.name

        def apply(self, selfp):
            if self.elt.body:
                for elt in self.elt.body:
                    if type(elt) is javalang.tree.MethodDeclaration:
                        selfp.MethodDeclaration(elt, self).visit(selfp)
                    elif type(elt) is javalang.tree.FieldDeclaration:
                        selfp.FieldDeclaration(elt, self).visit(selfp)
                    else:
                        if selfp.args.debug_ast:
                            logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
            for elt in self.elt.arguments:
                selfp.ClassCreatorParameters(elt, self).visit(selfp)
    
    class ClassCreatorParameters(BaseNode):
        
        #def getName(self):
        #    return self.__class__.__name__ + " : " +self.elt.value

        def apply(self, selfp):
            elt = self.elt
            if type(elt) is javalang.tree.ClassCreator:
                selfp.ClassCreator(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.BinaryOperation:
                selfp.BinaryOperation(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.MethodInvocation:
                selfp.MethodInvocation(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.Literal:
                selfp.Literal(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.MemberReference:
                selfp.MemberReference(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.MemberReference:
                selfp.MemberReference(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.This:
                selfp.This(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.Cast:
                selfp.Cast(elt, self).visit(selfp)
            else:
                if selfp.args.debug_ast:
                    logging.error("%s - %s" % (self.__class__.__name__, type(elt)))


    class SwitchStatement(BaseNode):

        def apply(self, selfp):
            self = self
            #print(self.elt.__dict__, end='')

    class DoStatement(BaseNode):

        def apply(self, selfp):
            self = self
            #print(self.elt.__dict__, end='')


    class MemberReference(BaseNode):

        def getName(self):
            return self.__class__.__name__ + " : " +self.elt.member

        def apply(self, selfp):
            pass

    
    class Cast(BaseNode):
        
        def getName(self):
            return self.__class__.__name__ + " : " +self.elt.type.name

        def apply(self, selfp):
            elt = [self.elt.expression]
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
                elif type(elt) is javalang.tree.ClassCreator:
                    selfp.ClassCreator(elt, self).visit(selfp)
                else:
                    if selfp.args.debug_ast:
                        logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
            
            if "selectors" in self.elt.__dict__:
                #elt.extend(self.elt.selectors)
                selfp.CastSelectors(self.elt.selectors, self).visit(selfp)
    
    class CastSelectors(BaseNode):

        def apply(self, selfp):
            for elt in self.elt:
                if type(elt) is javalang.tree.MethodInvocation:
                    selfp.MethodInvocation(elt, self).visit(selfp)
                else:
                    if selfp.args.debug_ast:
                        logging.error("%s - %s" % (self.__class__.__name__, type(elt)))


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
        
        def getName(self):
            return self.__class__.__name__ + " : " + self.elt.operator

        def apply(self, selfp):
            for elt in [self.elt.operandl, self.elt.operandr]:
                if type(elt) is javalang.tree.BinaryOperation:
                    selfp.BinaryOperation(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.MemberReference:
                    selfp.MemberReference(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.Literal:
                    selfp.Literal(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.MethodInvocation:
                    selfp.MethodInvocation(elt, self).visit(selfp)
                elif type(elt) is javalang.tree.This:
                    selfp.This(elt, self).visit(selfp)
                else:
                    if selfp.args.debug_ast:
                        logging.error("%s - %s" % (self.__class__.__name__, type(elt)))

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
            for elt in self.elt.initializers:
                if type(elt) is javalang.tree.Literal:
                    selfp.Literal(elt, self).visit(selfp)
                else:
                    if selfp.args.debug_ast:
                        logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
            pass

    class ArraySelector(BaseNode):

        def apply(self, selfp):
            pass

    class EnumBody(BaseNode):

        def apply(self, selfp):
            pass

    class VariableDeclarator(BaseNode):

        def getName(self):
            return self.__class__.__name__ + " : " + self.elt.name

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
            elif type(elt) is javalang.tree.Literal:
                selfp.Literal(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.TernaryExpression:
                selfp.TernaryExpression(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.BinaryOperation:
                selfp.BinaryOperation(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.This:
                selfp.This(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.ArrayCreator:
                selfp.ArrayCreator(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.ArrayInitializer:
                selfp.ArrayInitializer(elt, self).visit(selfp)
            elif type(elt) is javalang.tree.Assignment:
                selfp.Assignment(elt, self).visit(selfp)
            else:
                if selfp.args.debug_ast:
                    logging.error("%s - %s" % (self.__class__.__name__, type(elt)))
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

