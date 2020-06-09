from static.ast import *
from graphviz import Digraph
import javalang

# TODO: Add Capability to overload function
# 15 LoginFormState(Integer n, Integer n2) {
# 16         this.usernameError = n;
# 17         this.passwordError = n2;
# 18         this.isDataValid = false;
# 19     }
# 20
# 21     LoginFormState(boolean bl) {
# 22         this.usernameError = null;
# 23         this.passwordError = null;
# 24         this.isDataValid = bl;

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
"""
Convert javalang type Node in Ast Node
"""
def JavaLang2NodeAst(node : javalang.tree, parent : ast.BaseNode) -> Node:
    if type(node) is javalang.tree.This:
        return ast.This(node, parent)
    if type(node) is javalang.tree.MemberReference:
        return ast.MemberReference(node, parent)
    if type(node) is javalang.tree.MethodInvocation:
        return ast.MethodInvocation(node, parent)
    if type(node) is javalang.tree.Cast:
        return ast.Cast(node, parent)
    if type(node) is javalang.tree.ClassCreator:
        return ast.ClassCreator(node, parent)

"""
Add Assignment Edge with:
    - parent reference to left expression as child
    - parent reference to rigt expression as parent
"""
# TODO: Why child get and parent xref
@Node("Assignment", "in")
class AssignmentVarIn:
    @classmethod
    def call(cls, r, self):
        #print(self.elt.expressionl)
        # Seek Reference Node from left expression and store it in child
        path = revxref(JavaLang2NodeAst(self.elt.expressionl, self))
        child = TaintElt.get(path[:-1], path[-1])

        # Seek Reference Node from right expression and store it in parent
        # Remove Literral case
        if type(self.elt.value) is javalang.tree.Literal:
            parent = [] #self.elt.value
        else:
            path = revxref(JavaLang2NodeAst(self.elt.value, self))
            # Reference not found should probably there not in the scope
            if len(path) == 0:
                return r # No node influence here
            else:
                parent = xref(path[:-1], path[-1])
        # Create Node
        n = Node(path[-1], child, parent, self)

        # Add Node
        TaintElt.add_elt(
            TaintElt.get(
                TaintElt._Class,
                None)["__fields__"], n)

        # Add Childness
        if type(parent) is Node:
            parent.child(n)

        # Add Parentness
        child.parent(n)

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

"""
Convert node given in Type of this node
"""
def conv_type(path : list, node : str, child=False) -> list:
    nodes = TaintElt._nodes
    for p in path:
        # Not in scope to analyzed
        if not p in nodes:
            return path
        nodes = nodes[p]
    # If node is already a type return it
    if node in nodes:
        path.append(node)
        return path
    else:
        # If path is empty search in current scope
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


"""
Take path to access Node and give Node ref associated
"""
def xref(path : list, node : str) -> list:
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
                    assert True # Type not defined
                    #root.append(s)
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

"""
Go where the begining of the variable begin
"""
def up2Statement(node):
    root = [node]
    while type(root[-1].parent) in [ast.MethodInvocation,
                                    ast.MemberReference,
                                    ast.ArraySelector,
                                    ast.This]:
        root.append(root[-1].parent)
    return root[-1]

"""
From parent Ast Node to path to access
"""
def revxref(node : ast.BaseNode) -> list:
    #print(f"{node.elt}")
    assert node
    prev_type = []
    root = [node]
    last = None
    while len(root) > 0:
        e = root.pop()
        if type(e) is ast.MethodInvocation:
            if e.elt.qualifier:
                prev_type = conv_type(prev_type, e.elt.qualifier)
                if prev_type == None:
                    return []
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
            while len(prev_type_tmp) > 0:
                tmp = conv_type(prev_type_tmp, e.elt.member)
                if tmp:
                    break
                prev_type_tmp.pop()
            last = prev_type.copy()
            last.append(e.elt.member)
            last = (last, tmp)
            prev_type = tmp
            if tmp[-1] == "List":
                e2 = root.pop()
                if type(e2) is ast.ArraySelector:
                    prev_type = conv_type(prev_type, e.elt.member, child=True)
                else:
                    prev_type = tmp
                    root.append(e2)
    if last:
        if last[1] == prev_type:
            return last[0]
    return prev_type

"""
Like xref but give the type at the end and not the name
"""
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
                    child.parent(n)
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
        TaintElt.graphiz(orphan=False)
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
    def graphiz(cls, orphan=False):
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
                            if orphan or (len(sc.child_get()) > 0 or len(sc.parent_get()) > 0):
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
    def scope_print(cls, scope):
        if type(scope) is list:
            return "[" + ", ".join([cls.scope_print(e) for e in scope]) + "]"
        return str(scope)

    # PrettyPrint of graph
    @classmethod
    def print(cls, nodes=None, layers = 0):
        if not nodes:
            nodes = cls._nodes
        if type(nodes) is dict:
            for k, v in nodes.items():
                print("%s%s" % ("\t"* layers, k))
                cls.print(v, layers+1)
        else:
            for k in reversed(nodes):
                #print("%s%s" % ("\t"* layers, ", ".join([str(e) for e in k])))
                print("%s%s" % ("\t"* layers, cls.scope_print(k)))


    @classmethod
    def Class(cls, name, method=False):
        # Add scope Class
        cls._Class.append(name)
        cls._ClassType.append(method)
        cls.ConstructScope(cls._Class)

        cls.scope_p.append([-1])

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

        f = fields[-1]
        for sc in cls.scope_p[-1][:-1]:
                f = f[sc]
        if len(cls.scope_p[-1]) > 0:
            cls.scope_p[-1][-1] += 1
        f.append([])
        cls.scope_p[-1].append(-1)

    @classmethod
    def add_elt(cls, fields, elt):
        f = fields[-1]
        for sc in cls.scope_p[-1][:-1]:
            f = f[sc]
        f.append(elt)
        cls.scope_p[-1][-1] += 1

    @classmethod
    def new(cls, elt, name, parent, index=None):

        # Traversal graph
        nodes = cls._nodes
        for i in range(len(cls._Class) - 1):
            nodes = nodes[cls._Class[i]]
        #print(nodes)
        if index != None and len(nodes[cls._Class[-1]]["__fields__"][-1]) > index:
            # Update field (normaly for parameters)
            n = nodes[cls._Class[-1]]["__fields__"][-1][index]
            n.set(name)
            n.node(elt)
            cls.scope_p[-1][-1] += 1
        else:
            # Add field node for Method field
            n = Node(name, None, None, elt)
            #nodes[cls._Class[-1]]["__fields__"][-1].append(n)
            cls.add_elt(nodes[cls._Class[-1]]["__fields__"], n)

    
    @classmethod
    def get(cls, clazz, field):
        assert len(clazz) > 0 or field
        if len(clazz) == 0:
            clazz = cls._Class.copy()
        if field:
            nfield = []
        # Find node in graph
        nodes = cls._nodes
        for i in range(len(clazz)):
            if not clazz[i] in nodes:
                # class i not found
                return None
            nodes = nodes[clazz[i]]
            if field:
                nfield.append(nodes)
        if field:
            # if clazz empty current scope is taken
            while len(nfield) > 0:
                nodes = nfield.pop()
                for n in nodes["__fields__"][0]:
                    # TODO : n[0] is only the first layer
                    if type(n) is list:
                        if len(n) > 0 and not type(n[0]) is list and n[0].get() == field:
                            return n
                    else:
                        if n.get() == field:
                            return n
            return None
        return nodes

