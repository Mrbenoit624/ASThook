from static.ast import *
from graphviz import Digraph

@Node("MethodDeclaration", "in")
class MethodDeclarationIn:
    @classmethod
    def call(cls, r, self):
        # Add scope method
        TaintElt.Method(self.elt.name)
        # Create Node for each parameters
        for param in self.elt.parameters:
            TaintElt.new(self, param.name, None,
                    self.elt.parameters.index(param))
        return r

@Node("FieldDeclaration", "in")
class FieldDeclarationIn:
    @classmethod
    def call(cls, r, self):
        # Create Node for Fields
        TaintElt.new(self, self.elt.declarators[0].name, None)
        return r

#@Node("Assignment", "in")
#class MethodDeclarationIn:
#    @classmethod
#    def call(cls, r, self):
#        print(self.elt, end='\n\n')
#        return r


@Node("MethodInvocation", "in")
class MethodInvocationIn:
    @classmethod
    def call(cls, r, self):
        # Add status for enumerate parameters of this function
        # parameters_function will be use in MemberReference
        TaintElt.status.append(("parameters_function", self, 0))
        return r

@Node("MethodInvocation", "out")
class MethodInvocationIn:
    @classmethod
    def call(cls, r, self):
        # Remove status for enumerate parameters of this function
        TaintElt.status.pop()
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

@Node("MemberReference", "in")
class MemberReferenceIn:
    @classmethod
    def call(cls, r, self):
        if len(TaintElt.status) > 0:
            k, v, i = TaintElt.status[-1]
            if k == "parameters_function":
                if type(v.parent) is ast.This:
                    # found variable which call the method 'm'
                    clazz, member = ThisAttribute(v.parent)
                    n = TaintElt.get(clazz, [],
                        member)
                    if n:
                        #found parameters node of the method 'm'
                        n = TaintElt.get([n.node_get().elt.type.name],
                                [v.elt.member], None)["__fields__"][0][-(i+1)]
                        if type(self.parent) is ast.This:
                            # found node of argument in parameters
                            clazz2, member = ThisAttribute(self.parent)
                            n2 = TaintElt.get(clazz2,
                                    TaintElt._Method[:len(clazz2)-1], member)
                            # add node as child
                            n2.child(n)
                            n.parent(n2)
                            print(self.elt)
                    #TaintElt.add_from_function(self,
                    #        self.elt.member,
                    #        TaintElt._Class[-1],
                    #        v.elt.member,
                    #        i)
            TaintElt.status[-1] = (k, v, i + 1)

        #print(self.elt, end='\n\n')
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
        TaintElt.OutMethod()
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
        ret = f"{self._elt}:{self._node.elt._position}"
        if not len(self._child) == 0:
            ret += " -> { " + ",".join(str(x) for x in self._child) + " }"
        return ret
    
    def node(self, node):
        self._node = node
    
    def node_get(self):
        return self._node

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

class TaintElt:

    @classmethod
    def graphiz(cls):
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
                            print(str(i.node_get()) + " " + str(i))
                            dot.node(str(i.node_get())+str(i.get()), i.get())
                            for e in i.child_get():
                                dot.edge(
                                        str(i.node_get())+str(i.get()),
                                        str(e.node_get())+str(e.get()),
                                        color="blue")
                                print(e.node_get())
                            for e in i.parent_get():
                                dot.edge(
                                        str(i.node_get())+str(i.get()),
                                        str(e.node_get())+str(e.get()),
                                        color="red")
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
                                print(str(i[i2].node_get()) + " " + str(i[i2]))
                                dot.node(str(i[i2].node_get())+str(i[i2].get()),
                                        i[i2].get())
                                for e in i[i2].child_get():
                                    dot.edge(
                                            str(i[i2].node_get())+str(i[i2].get()),
                                            str(e.node_get())+str(e.get()),
                                            color="blue")
                                    print(e.node_get())
                                for e in i[i2].parent_get():
                                    dot.edge(
                                            str(i[i2].node_get())+str(i[i2].get()),
                                            str(e.node_get())+str(e.get()),
                                            color="red"
                                            )
        dot.render("taint/Taint")

    # PrettyPrint of graph
    @classmethod
    def print(cls, nodes=None, layers = 0):
        if not nodes:
            nodes = cls._nodes
        for k, v in nodes.items():
            print("%s%s" % ("\t"* layers*2, k))
            if type(v) is list:
                for j in range(len(v)):
                    for i in v[j]:
                        print("%s\t%s" % ("\t" *(layers*2+j),i))
                continue
            for k2, v2 in v.items():
                print("%s\t%s" % ("\t" * layers*2, k2))
                if type(v2) is dict:
                    cls.print(v2, layers+1)
                else:
                    for i in v2:
                        for i2 in range(len(i)):
                            print("%s\t\t%s" % ("\t" * layers*2, i[i2]))

    @classmethod
    def Class(cls, name):
        # Add scope Class
        cls._Class.append(name)
        # Traversal graph
        nodes = cls._nodes
        for i in range(len(cls._Class) - 1):
            nodes = nodes[cls._Class[i]][cls._Method[i]]

        # Add node Class with field and scope field
        nodes[cls._Class[-1]] = {}
        nodes[cls._Class[-1]]["__fields__"] = []
        nodes[cls._Class[-1]]["__fields__"].append([])

    @classmethod
    def OutClass(cls):
        cls._Class.pop()
    
    @classmethod
    def Method(cls, name):
        # Add scope Method
        cls._Method.append(name)
        # Traversal graph
        nodes = cls._nodes
        for i in range(len(cls._Class) - 1):
            nodes = nodes[cls._Class[i]][cls._Method[i]]

        # Add node Method with field and scope field
        nodes[cls._Class[-1]][name] = {}
        nodes[cls._Class[-1]][name]["__fields__"] = []
        nodes[cls._Class[-1]][name]["__fields__"].append([])
    
    @classmethod
    def OutMethod(cls):
        cls._Method.pop()


    @classmethod
    def Init(cls):
        cls._nodes = {}
        cls.status = []
        cls._Class = []
        cls._Method =[]

    @classmethod
    def new(cls, elt, name, parent, index=None):

        # Traversal graph
        nodes = cls._nodes
        for i in range(len(cls._Class) - 1):
            nodes = nodes[cls._Class[i]][cls._Method[i]]

        if len(cls._Method) != len(cls._Class):
            # Add field node for class field
            nodes[cls._Class[-1]]["__fields__"][-1].append(Node(name,
                None,
                None,
                elt))
        elif index and len(nodes[cls._Class[-1]][cls._Method[-1]]["__fields__"][-1]) > index:
            # Update field (normaly for parameters)
            n = nodes[cls._Class[-1]][cls._Method[-1]]["__fields__"][-1][index]
            n.set(name)
            n.node(elt)
        else:
            # Add field node for Method field
            n = Node(name, None, None, elt)
            nodes[cls._Class[-1]][cls._Method[-1]]["__fields__"][-1].append(n)

    #@classmethod
    #def add(cls, elt, name):
    #    if not cls._Method:
    #        return 
    #    for e in cls._nodes[cls._Class][cls._Method][-1]:
    #        if e.get() == name:
    #            n = Node(name, None, e, elt._position)
    #            e.child(n)
    
    @classmethod
    def get(cls, clazz, func, field):
        # Find node in graph
        nodes = cls._nodes
        for i in range(len(clazz)):
            if not clazz[i] in nodes:
                # class i not found
                return None
            nodes = nodes[clazz[i]]
            if i < len(func):
                if not func[i] in nodes:
                    # method i not found
                    return None
                nodes = nodes[func[i]]
        if field:
            for n in nodes["__fields__"][0]:
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
