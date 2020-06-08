from static.ast import *
from graphviz import Digraph
import javalang

@Node("ConstructorDeclarationParameters", "in")
class ConstructorDeclarationIn:
    @classmethod
    def call(cls, r, self):
        TaintElt.new(self, self.elt.name, None,
                index=self.parent.elt.parameters.index(self.elt))
        return r

@Node("ConstructorDeclaration", "in")
class ConstructorDeclarationIn:
    @classmethod
    def call(cls, r, self):
        # Add scope method
        TaintElt.Class(self.elt.name, True)
        return r

@Node("ConstructorDeclaration", "out")
class ConstructorDeclarationOut:
    @classmethod
    def call(cls, r, self):
        # Add scope method
        TaintElt._Class.pop()
        return r

@Node("MethodDeclaration", "in")
class MethodDeclarationIn:
    @classmethod
    def call(cls, r, self):
        # Add scope method
        TaintElt.Class(self.elt.name, True)
        return r

@Node("MethodDeclarationParameters", "in")
class MethodDeclarationParametersIn:
    @classmethod
    def call(cls, r, self):
        TaintElt.new(self, self.elt.name, None,
                self.parent.elt.parameters.index(self.elt))
        return r


@Node("FieldDeclaration", "in")
class FieldDeclarationIn:
    @classmethod
    def call(cls, r, self):
        # Create Node for Fields
        TaintElt.new(self, self.elt.declarators[0].name, None)
        return r

@Node("VariableDeclarator", "in")
class VariableDeclaratorIn:

    @classmethod
    def call(cls, r, self):
        TaintElt.new(self.parent, self.elt.name, None)
        return r

def JavaLang2NodeAst(node, parent):
    if type(node) is javalang.tree.This:
        return ast.This(node, parent)
    if type(node) is javalang.tree.MemberReference:
        return ast.MemberReference(node, parent)

@Node("Assignment", "in")
class AssignmentVarIn:
    @classmethod
    def call(cls, r, self):
        print("##################################################")
        #print(self.elt.expressionl)
        path = revxref(JavaLang2NodeAst(self.elt.expressionl, self))
        child = TaintElt.get(path[:-1], path[-1])
        if type(self.elt.value) is javalang.tree.Literal:
            parent = [] #self.elt.value
        else:
            path = revxref(JavaLang2NodeAst(self.elt.value, self))
            parent = xref(path[:-1], path[-1])
        n = Node(path[-1], child,parent , self)
        TaintElt.add_elt(
            TaintElt.get(
                TaintElt._Class,
                None)["__fields__"], n)
        if type(parent) is Node:
            parent.child(n)

        print("##################################################")
        #print(xref([], self.elt.expressionl))
        #print(self.elt, end='\n\n')
        #TaintElt.status.append(("assignement_var", self, 9))
        return r

@Node("AssignmentVar", "out")
class AssignmentVarOut:
    @classmethod
    def call(cls, r, self):
        #TaintElt.status.pop()
        return r


@Node("MethodInvocation", "in")
class MethodInvocationIn:
    @classmethod
    def call(cls, r, self):
        # Add status for enumerate parameters of this function
        # parameters_function will be use in MemberReference
        TaintElt.status.append(("parameters_function", self, 0))
        #print(TaintElt._Class)
        nodes = TaintElt.get(TaintElt._Class, None)
        TaintElt.add_scope(nodes["__fields__"])
        return r

@Node("MethodInvocation", "out")
class MethodInvocationIn:
    @classmethod
    def call(cls, r, self):
        # Remove status for enumerate parameters of this function
        TaintElt.status.pop()
        TaintElt.scope_p[-1].pop()
        return r

@Node("MethodInvocationParameters", "out")
class MethodInvocationParametersOut:
    @classmethod
    def call(cls, r, self):
        k, v, i = TaintElt.status[-1]
        TaintElt.status[-1] = (k, v, i + 1)
        return r

@Node("ClassCreator", "in")
class ClassCreatorIn:
    @classmethod
    def call(cls, r, self):
        TaintElt.status.append(("parameters_class", self, 0))
        if self.elt.body:
            # Add scope for class
            TaintElt.Class(self.elt.type.name)
        return r

@Node("ClassCreator", "out")
class ClassDeclarationOut:
    @classmethod
    def call(cls, r, self):
        TaintElt.status.pop()
        if self.elt.body:
            # remove last class scope
            TaintElt.OutClass()
        return r

def ThisAttribute(node):
    # get attribute of node
    # example:
    #  - This.hello() -> (CurrentClass, hello)
    #  - This.hello -> (CurrentClass, hello)
    #  - ToTo.This.hello -> (ToTo, hello)
    if type(node) is ast.This:
        clazz = node.elt.qualifier
        field = node.elt.selectors[0].member
        clazz = [clazz] if clazz else TaintElt._Class
        return (clazz, field)

def conv_typebak(path, node, child=False):
    nodes = TaintElt._nodes
    for p in path:
        nodes = nodes[p]
    if node in nodes:
        path.append(node)
        return path
    else:
        if len(path) == 0:
            path = TaintElt._Class[:-1] if TaintElt._Class[-1] else TaintElt._Class
            for p in path:
                nodes = nodes[p]
        for n in nodes["__fields__"][0]:
            if n.get() == node:
                if child:
                    return [n.node_get().elt.type.arguments[0].type.name]
                return [n.node_get().elt.type.name]

def conv_type(path, node, child=False):
    nodes = TaintElt._nodes
    for p in path:
        # Not in scope to analyzed
        if not p in nodes:
            return path
        nodes = nodes[p]
    if node in nodes:
        path.append(node)
        return path
    else:
        if len(path) == 0:
            path = TaintElt._Class
            nodes_ = nodes
            while len(path) > 0:
                nodes = nodes_
                for p in path:
                    nodes = nodes[p]
                for n in nodes["__fields__"][0]:
                    if type(n) is list:
                        continue
                    if n.get() == node:
                        if child:
                            return [n.node_get().elt.type.arguments[0].type.name]
                        return [n.node_get().elt.type.name]
                path = path[:-1]
        else:
            for n in nodes["__fields__"][0]:
                if type(n) is list:
                    continue
                if n.get() == node:
                    if child:
                        return [n.node_get().elt.type.arguments[0].type.name]
                    return [n.node_get().elt.type.name]



def xref(path, node):
    prev_type = []
    root = path
    while len(root) > 0:
        e = root.pop()
        if type(e) is ast.MethodInvocation:
            if e.elt.qualifier:
                prev_type = conv_type(prev_type, e.elt.qualifier)
                #prev_type.append(e.elt.qualifier)
            prev_type = conv_type(prev_type, e.elt.member)
        elif type(e) is ast.This:
            prev_type.extend(TaintElt._Class[:-1] if TaintElt._Class[-1] else TaintElt._Class)
            for s in reversed(e.elt.selectors):
                if type(s) is javalang.tree.MemberReference:
                    root.append(ast.MemberReference(s, e))
                elif type(s) is javalang.tree.ArraySelector:
                    root.append(ast.ArraySelector(s, e))
                elif type(s) is javalang.tree.MethodInvocation:
                    root.append(ast.MethodInvocation(s, e))
                else:
                    root.append(s)
        elif type(e) is ast.ArraySelector:
            pass # No incidence
        elif type(e) is ast.MemberReference:
            tmp = conv_type(prev_type, e.elt.member)
            if tmp[-1] == "List":
                e2 = root.pop()
                if type(e2) is ast.ArraySelector:
                    prev_type = conv_type(prev_type, e.elt.member, child=True)
                else:
                    prev_type = tmp
                    root.append(e2)
    if len(prev_type) == 0:
        prev_type = TaintElt._Class.copy()
    while len(prev_type) > 0:
        ret = TaintElt.get(prev_type, node)
        if ret:
            return ret
        prev_type.pop()
    #for elt in TaintElt.get(prev_type, None)["__fields__"][0]:
    #    print(elt)

def up2Statement(node):
    root = [node]
    while type(root[-1].parent) in [ast.MethodInvocation,
                                    ast.MemberReference,
                                    ast.ArraySelector,
                                    ast.This]:
        root.append(root[-1].parent)
    return root[-1]

def revxref(node):
    prev_type = []
    root = [node]
    while len(root) > 0:
        e = root.pop()
        if type(e) is ast.MethodInvocation:
            if e.elt.qualifier:
                prev_type = conv_type(prev_type, e.elt.qualifier)
                #prev_type.append(e.elt.qualifier)
            prev_type = conv_type(prev_type, e.elt.member)
        elif type(e) is ast.This:
            prev_type.extend(TaintElt._Class[:-1] if TaintElt._ClassType[-1] else TaintElt._Class)
            for s in reversed(e.elt.selectors):
                if type(s) is javalang.tree.MemberReference:
                    root.append(ast.MemberReference(s, e))
                elif type(s) is javalang.tree.ArraySelector:
                    root.append(ast.ArraySelector(s, e))
                elif type(s) is javalang.tree.MethodInvocation:
                    root.append(ast.MethodInvocation(s, e))
                else:
                    root.append(s)
        elif type(e) is ast.ArraySelector:
            pass # No incidence
        elif type(e) is ast.MemberReference:
            if len(root) == 0:
                prev_type.append(e.elt.member)
                return prev_type
            prev_type_tmp = prev_type.copy()
            last = e.elt.member
            while len(prev_type_tmp) > 0:
                tmp = conv_type(prev_type_tmp, e.elt.member)
                if tmp:
                    break
                prev_type_tmp.pop()
            prev_type = tmp
            if tmp[-1] == "List":
                e2 = root.pop()
                if type(e2) is ast.ArraySelector:
                    prev_type = conv_type(prev_type, e.elt.member, child=True)
                else:
                    prev_type = tmp
                    root.append(e2)
    return prev_type

def get_type(node):
    prev_type = []
    root = [node]
    #while type(root[-1].parent) in [ast.MethodInvocation,
    #                                ast.MemberReference,
    #                                ast.ArraySelector,
    #                                ast.This]:
    #    root.append(root[-1].parent)
    #root = [root[-1]]
    while len(root) > 0:
        e = root.pop()
        if type(e) is ast.MethodInvocation:
            if e.elt.qualifier:
                prev_type = conv_type(prev_type, e.elt.qualifier)
                #prev_type.append(e.elt.qualifier)
            #prev_type = conv_type(prev_type, e.elt.member)
            tmp_type = conv_type(prev_type, e.elt.member)
            if not tmp_type:
                prev_type.append(e.elt.member)
                TaintElt.ConstructScope(prev_type)
            else:
                prev_type = tmp_type
        elif type(e) is ast.This:
            prev_type.extend(TaintElt._Class[:-1] if TaintElt._ClassType[-1] else TaintElt._Class)
            for s in reversed(e.elt.selectors):
                if type(s) is javalang.tree.MemberReference:
                    root.append(ast.MemberReference(s, e))
                elif type(s) is javalang.tree.ArraySelector:
                    root.append(ast.ArraySelector(s, e))
                elif type(s) is javalang.tree.MethodInvocation:
                    root.append(ast.MethodInvocation(s, e))
                else:
                    root.append(s)
        elif type(e) is ast.ArraySelector:
            pass # No incidence
        elif type(e) is ast.MemberReference:
            prev_type_tmp = prev_type.copy()
            while len(prev_type_tmp) > 0:
                tmp = conv_type(prev_type_tmp, e.elt.member)
                if tmp:
                    break
                prev_type_tmp.pop()
            prev_type = tmp
            if tmp[-1] == "List":
                e2 = root.pop()
                if type(e2) is ast.ArraySelector:
                    prev_type = conv_type(prev_type, e.elt.member, child=True)
                else:
                    prev_type = tmp
                    root.append(e2)

            
            #print(f"{e.elt.qualifier}.{e.elt.member}")
    #print(".".join(prev_type))
    return prev_type

    pass

@Node("MemberReference", "in")
class MemberReferenceIn:
    @classmethod
    def call(cls, r, self):
        if len(TaintElt.status) > 0:
            k, v, i = TaintElt.status[-1]
            if k == "parameters_function":
                child = TaintElt.get(get_type(up2Statement(v)), None)
                if child:
                    if len(child["__fields__"][0]) <= i:
                        n = Node(None, [], [], self)
                        child["__fields__"][0].append(n)
                    child = child["__fields__"][0][i]
                    #print(get_type(self.elt.member))
                    #print(conv_type([], self.elt.member))
                    parent = xref([], self.elt.member)
                    n = Node(self.elt.member, child,parent , self)
                    TaintElt.add_elt(
                        TaintElt.get(
                            TaintElt._Class,
                            None)["__fields__"], n)
                    parent.child(n)
            #elif k == "assignement_var":
            #    parent = xref([],self.elt.member)
                #n = Node(self.elt.member, child,parent , self)
        return r


@Node("ClassDeclaration", "in")
class ClassDeclarationIn:
    @classmethod
    def call(cls, r, self):
        # Add node Class and scope Class
        TaintElt.Class(self.elt.name)
        return r

@Node("ClassDeclaration", "out")
class ClassDeclarationOut:
    @classmethod
    def call(cls, r, self):
        # Remove last Class scope
        TaintElt.OutClass()
        return r

@Node("MethodDeclaration", "out")
class MethodDeclarationOut:
    @classmethod
    def call(cls, r, self):
        # Remove last Method scope
        #TaintElt.OutMethod()
        TaintElt.OutClass()
        return r

@Node("Init", "in")
class Init:
    @classmethod
    def call(cls, r, path):
        TaintElt.Init()
        return r

@Node("Init", "out")
class InitOut:
    @classmethod
    def call(cls, r, path):
        TaintElt.print()
        TaintElt.graphiz()
        return r


class Node:

    def __init__(self, elt, child, parent, node=None):
        self.set(elt)
        self._child = []
        self.child(child)
        self._parent = []
        self.parent(parent)
        self.node(node)

    def __str__(self):
        #ret = f"{self._elt}:{self._node.elt._position} {p_n(self._node)}"
        ret = f"{self._elt}:{self.position()}"
        if not len(self._child) == 0:
            #ret += " -> { " + ",".join(str(x) for x in self._child) + " }"
            ret += " -> {" + ",".join(str(x.get()) for x in self._child) + "}"
        return ret
    
    def node(self, node):
        self._node = node

    def id(self):
        return p_n(self._node)
    
    def node_get(self):
        return self._node

    def position(self):
        return self._node.elt._position if "_position" in self._node.elt.__dict__ else ""

    def parent_get(self):
        return self._parent

    def child_get(self):
        return self._child

    def get(self):
        return self._elt

    def parent(self, parent):
        if not parent:
            return
        if type(parent) is list:
            self._parent.extend(parent)
        else:
            self._parent.append(parent)

    def child(self, child):
        if not child:
            return
        if type(child) is list:
            self._child.extend(child)
        else:
            self._child.append(child)

    def set(self, elt):
        self._elt = elt

def p_n(node):
    return str(hex(id(node)))

class TaintElt:

    @classmethod
    def graphiz(cls):
        dot = Digraph(comment="test")
        dot.attr('node', shape='box')
        dot.attr('graph', splines='ortho')
        nodesq = [(cls._nodes, [])]
        while len(nodesq) > 0:
            nodes, base = nodesq.pop()
            if type(nodes) is dict:
                for k, v in nodes.items():
                    nbase = base.copy()
                    nbase.append(k)
                    nodesq.append((v, nbase))
            else:
                for k in reversed(nodes):
                    scopes = [k]
                    while len(scopes) > 0:
                        sc = scopes.pop()
                        if type(sc) is list:
                            for i in sc:
                                scopes.append(i)
                        else:
                            dot.node(f"{sc.id()}_{sc.get()}",
                                    "%s\n%s\n%s" % (
                                        sc.get(),
                                        sc.position(),
                                        ".".join(base[:-1])))
                            for e in sc.child_get():
                                dot.edge(
                                        f"{sc.id()}_{sc.get()}",
                                        f"{e.id()}_{e.get()}",
                                        color="blue")
        dot.render("taint/Taint")

                    #print("%s%s" % ("\t"* layers, ", ".join([str(e) for e in k])))
                    #print("%s%s" % ("\t"* layers, cls.scope_print(k)))

    @classmethod
    def graphizbak(cls):
        dot = Digraph(comment="test")
        dot.attr('node', shape='box')
        dot.attr('graph', splines='ortho')
        nodesq = [(cls._nodes, "")]
        while len(nodesq) > 0:
            nodes, base = nodesq.pop()
            for k, v in nodes.items():
                #print(k)
                if type(v) is list:
                    for j in range(len(v)):
                        for i in v[j]:
                            #print(f"{base}{k}{i}")
                            #print(p_n(i.node_get()) + " " + str(i))
                            dot.node(f"{i.id()}_{i.get()}",
                                    i.get())
                            for e in i.child_get():
                                dot.edge(
                                        f"{i.id()}_{i.get()}",
                                        f"{e.id()}_{e.get()}",
                                        color="blue")
                                #print(e.node_get())
                            #for e in i.parent_get():
                            #    dot.edge(
                            #            f"{p_n(i.node_get())}_{i.get()}",
                            #            f"{p_n(e.node_get())}_{e.get()}",
                            #            color="red")
                            pass
                    continue
                for k2, v2 in v.items():
                    #print("%s\t%s" % ("\t" * layers*2, k2))
                    if type(v2) is dict:
                        nodesq.append((v2, f"{base}{k}{k2}"))
                    else:
                        for i in v2:
                            for i2 in range(len(i)):
                                #print(f"{base}{k}{k2}{i[i2]}")
                                #print(p_n(i[i2].node_get()) + " " + str(i[i2]))
                                dot.node(f"{i[i2].id()}_{i[i2].get()}",
                                        i[i2].get())
                                for e in i[i2].child_get():
                                    dot.edge(
                                        f"{i[i2].id()}_{i[i2].get()}",
                                        f"{e.id()}_{e.get()}",
                                        color="blue")
                                    #print(e.node_get())
                                #for e in i[i2].parent_get():
                                #    dot.edge(
                                #        f"{p_n(i[i2].node_get())}_{i[i2].get()}",
                                #        f"{p_n(e.node_get())}_{e.get()}",
                                #        color="red")
        dot.render("taint/Taint")

    @classmethod
    def scope_print(cls, scope):
        if type(scope) is list:
            return "[" + ", ".join([cls.scope_print(e) for e in scope]) + "]"
        return str(scope)
    # PrettyPrint of graph
    @classmethod
    def print(cls, nodes=None, layers = 0):
        if not nodes:
            nodes = cls._nodes
            print(nodes)
        if type(nodes) is dict:
            for k, v in nodes.items():
                print("%s%s" % ("\t"* layers, k))
                cls.print(v, layers+1)
        else:
            for k in reversed(nodes):
                #print("%s%s" % ("\t"* layers, ", ".join([str(e) for e in k])))
                print("%s%s" % ("\t"* layers, cls.scope_print(k)))

        #if not nodes:
        #    nodes = cls._nodes
        #for k, v in nodes.items():
        #    print("%s%s" % ("\t"* layers*2, k))
        #    if type(v) is list:
        #        for j in range(len(v)):
        #            for i in v[j]:
        #                print("%s\t%s" % ("\t" *(layers*2+j),i))
        #        continue
        #    for k2, v2 in v.items():
        #        print("%s\t%s" % ("\t" * layers*2, k2))
        #        if type(v2) is dict:
        #            cls.print(v2, layers+1)
        #        else:
        #            for i in v2:
        #                for i2 in range(len(i)):
        #                    print("%s\t\t%s" % ("\t" * layers*2, i[i2]))

    @classmethod
    def Class(cls, name, method=False):
        # Add scope Class
        cls._Class.append(name)
        cls._ClassType.append(method)
        cls.ConstructScope(cls._Class)
        ## Traversal graph
        #nodes = cls._nodes
        #for i in range(len(cls._Class) - 1):
        #    nodes = nodes[cls._Class[i]]

        ## Add node Class with field and scope field
        #nodes[cls._Class[-1]] = {}
        #nodes[cls._Class[-1]]["__fields__"] = [[]]
        cls.scope_p.append([-1])
        #cls.add_scope(nodes[cls._Class[-1]]["__fields__"])
        #nodes[cls._Class[-1]]["__fields__"].append([])

    @classmethod
    def ConstructScope(cls, path):
        # Traversal graph
        nodes = cls._nodes
        for i in range(len(path) - 1):
            nodes = nodes[path[i]]
        if path[-1] in nodes:
            return
        # Add node Class with field and scope field
        nodes[path[-1]] = {}
        nodes[path[-1]]["__fields__"] = [[]]

    @classmethod
    def OutClass(cls):
        cls._Class.pop()
        cls._ClassType.pop()
        cls.scope_p.pop()

    @classmethod
    def OutMethod(cls):
        cls._Method.pop()


    @classmethod
    def Init(cls):
        # Graph of node Taint
        cls._nodes = {}
        # Status What should be done with MemberReference
        cls.status = []
        # Path of actual Node Class.Function
        cls._Class = []
        # Type of each element of _Class True if method else Class
        cls._ClassType = []
        cls.scope_p = []

    @classmethod
    def add_scope(cls, fields):

        #print(cls.scope_p, end=' ')
        #print(fields)
        f = fields[-1]
        #print(cls.scope_p)
        for sc in cls.scope_p[-1][:-1]:
                f = f[sc]
        if len(cls.scope_p[-1]) > 0:
            cls.scope_p[-1][-1] += 1
        f.append([])
        #print(f, end=' ')
        cls.scope_p[-1].append(-1)
        #print(fields, end=' ')
        #print(cls.scope_p)

    @classmethod
    def add_elt(cls, fields, elt):
        #print(cls.scope_p, end='-')
        #print(fields)
        f = fields[-1]
        for sc in cls.scope_p[-1][:-1]:
            f = f[sc]
        #print("---------------------------------")
        #print(f)
        #print(fields[-1])
        #TaintElt.print()
        f.append(elt)
        cls.scope_p[-1][-1] += 1
        #print(cls.scope_p, end='-')
        #print(fields)

    @classmethod
    def new(cls, elt, name, parent, index=None):

        # Traversal graph
        nodes = cls._nodes
        for i in range(len(cls._Class) - 1):
            nodes = nodes[cls._Class[i]]
        #print(nodes)
        if index != None and len(nodes[cls._Class[-1]]["__fields__"][-1]) > index:
            # Update field (normaly for parameters)
            print(index)
            n = nodes[cls._Class[-1]]["__fields__"][-1][index]
            n.set(name)
            n.node(elt)
            cls.scope_p[-1][-1] += 1
        else:
            # Add field node for Method field
            n = Node(name, None, None, elt)
            #nodes[cls._Class[-1]]["__fields__"][-1].append(n)
            cls.add_elt(nodes[cls._Class[-1]]["__fields__"], n)

    #@classmethod
    #def add(cls, elt, name):
    #    if not cls._Method:
    #        return 
    #    for e in cls._nodes[cls._Class][cls._Method][-1]:
    #        if e.get() == name:
    #            n = Node(name, None, e, elt._position)
    #            e.child(n)
    
    @classmethod
    def get(cls, clazz, field):
        # Find node in graph
        nodes = cls._nodes
        for i in range(len(clazz)):
            if not clazz[i] in nodes:
                # class i not found
                return None
            nodes = nodes[clazz[i]]
        if field:
            for n in nodes["__fields__"][0]:
                # TODO : n[0] is only the first layer
                if type(n) is list:
                    if len(n) > 0 and n[0].get() == field:
                        return n
                else:
                    if n.get() == field:
                        return n
            return None
        return nodes

                    
    #@classmethod
    #def add_from_function(cls, elt, name, clazz, function, arguments):
    #    nodes = cls._nodes
    #    for i in range(len(cls._Class) - 1):
    #        nodes = nodes[cls._Class[i]][cls._Method[i]]
    #    
    #    #print(nodes)
    #    #print(name)
    #    #print(clazz)
    #    #print(function)
    #    if not function in nodes[clazz]:
    #        nodes[clazz][function] = []
    #        nodes[clazz][function].append([])
    #        scope = nodes[cls._Class[-1]][cls._Method[-1]]["__fields__"][-1]
    #        try:
    #            #print(scope)
    #            parent = scope[scope.index(name)]
    #            n = Node(None, None, None, None)
    #        except ValueError as e:
    #            #print(e)
    #            #print(elt.elt._position)
    #            pass
    #    #print(cls._nodes[clazz][function][arguments])
