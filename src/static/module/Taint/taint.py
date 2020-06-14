from static.ast import *
from graphviz import Digraph
import javalang
from logging import debug, info

# TODO: Add Interface managing

@Node("ConstructorDeclarationParameters", "in")
class ConstructorDeclarationParametersIn:
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
        declaration_method(self)
        return r

@Node("ConstructorDeclaration", "out")
class ConstructorDeclarationOut:
    @classmethod
    def call(cls, r, self):
        # Add scope method
        TaintElt._Class.pop()
        TaintElt._ClassType.pop()
        return r

@Node("MethodDeclaration", "in")
class MethodDeclarationIn:
    @classmethod
    def call(cls, r, self):
        # Add scope method
        declaration_method(self)
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
        if self.elt.initializer == None:
            return r
        parent = ref_assignment(self.elt.initializer, self)
        if len(parent) > 0:
            n = TaintElt.get(TaintElt._Class, self.elt.name)
            for p in parent:
                n.parent(p)
                p.child(n)
        return r

"""
Add Assignment Edge with:
    - parent reference to left expression as child
    - parent reference to rigt expression as parent
"""
# TODO: Why child get and parent xref
@Node("Assignment", "in")
class AssignmentIn:
    @classmethod
    def call(cls, r, self):
        #print(self.elt.expressionl)
        # Seek Reference Node from left expression and store it in child
        path = revxref(JavaLang2NodeAst(self.elt.expressionl, self))
        if len(path) == 0:
            return r
        child = TaintElt.get(path[:-1], path[-1])
        if not child:
            return r
        node_name = path[-1]

        # Seek Reference Node from right expression and store it in parent
        parent = ref_assignment(self.elt.value, self)
        
        # Create Node
        n = Node(node_name, child, None, self)

        # Add Childness
        for p in parent:
            p.child(n)
            n.parent(p)

        # Add Node
        TaintElt.add_elt(
            TaintElt.get(
                TaintElt._Class,
                None)["__fields__"], n)


        # Add Parentness
        child.parent(n)

        return r


@Node("MethodInvocation", "in")
class MethodInvocationIn:
    @classmethod
    def call(cls, r, self):
        # Add status for enumerate parameters of this function
        # parameters_function will be use in MemberReference

        # Get argument type of method Invocation
        types_meth_invok = get_types_arguments(self.elt.arguments, self)
        
        # Get path to access at node of method
        path = revxref(up2Statement(self), stop=self)
        if path == ["None"]:
            return r
        
        #If element in current Scope
        if len(path) == 1:
            for i in reversed(range(len(TaintElt._ClassType))):
                if not TaintElt._ClassType[i]:
                    npath = TaintElt._Class[:i+1].copy()
                    npath.append(path[-1])
                    path = npath
                    break

        # Check if path is in scope to analyse
        if len(path) == 0:
            return r
        if not path[0] in TaintElt._nodes:
            return r
        n = TaintElt._nodes
        for i in path[:-1]:
            if i in n:
                n = n[i]
            else:
                return r

        path[-1] = "$" + "|".join(str(s) for s in types_meth_invok) + "$$" + path[-1]
        TaintElt.ConstructScope(path)

        signature = False
        for k, v in list(TaintElt.get(path[:-1], None).items())[1:]:
            if signature:
                break
            # if no begin with $ this is a subclass
            if not k[0] == '$':
                continue
            # split types arguments and method
            types, method = k[1:].split('$$')
            if not method == self.elt.member:
                continue
            # split types of arguments
            types = [] if len(types) == 0 else (types.split('|') if '|' in types else [types])
            # If signature have not the same number of arguments skip
            if not len(types) == len(types_meth_invok):
                continue
            # Check signature arguments
            signature = True
            for i_type in range(len(types)):
                if not types[i_type] == types_meth_invok[i_type]:
                    if not types_meth_invok[i_type] == None:
                        signature = False
            if not signature:
                continue
            # Replace the path by the good signature
            path[-1] = k
            for i in range(len(self.elt.arguments)):
                argument = self.elt.arguments[i]
                if len(TaintElt.get(path, None)["__fields__"][0]) == i:
                    n = Node(None, [], [], self)
                    TaintElt.get(path, None)["__fields__"][0].append(n)
                if not type(argument) is javalang.tree.Literal:
                    path_p = revxref(JavaLang2NodeAst(argument, self))
                    if len(path_p) == 0:
                        continue
                    parent = xref(path_p[:-1], path_p[-1])
                    # parent not a variable
                    if not type(parent) is Node:
                        continue

                    child = TaintElt.get(path, None)["__fields__"][0][i]
                    node = Node(path_p[-1], child, parent,
                            JavaLang2NodeAst(argument, self))
                    TaintElt.add_elt(
                        TaintElt.get(
                            TaintElt._Class,
                            None)["__fields__"], node)
                    child.parent(node)
                    parent.child(node)
        
        assert signature # signature of the function not found
        return r

@Node("MethodInvocation", "out")
class MethodInvocationOut:
    @classmethod
    def call(cls, r, self):
        # Remove status for enumerate parameters of this function
        #TaintElt.status.pop()
        #TaintElt.scope_p[-1].pop()
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
        return r


@Node("ClassDeclaration", "in")
class ClassDeclarationIn:
    @classmethod
    def call(cls, r, self):
        # Add node Class and scope Class
        TaintElt.Class(self.elt.name)
        return r

@Node("InterfaceDeclaration", "in")
class InterfaceDeclarationIn:
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
        #TaintElt.print()
        #info("Rendering taint analysis on pdf...")
        #TaintElt.graphiz(orphan=False)
        return r



################################################################################
#
#                           FUNCTIONS
#
################################################################################






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
    if type(node) is javalang.tree.ClassReference:
        return ast.ClassReference(node, parent)
    if type(node) is javalang.tree.ArrayCreator:
        return ast.ArrayCreator(node, parent)
    if type(node) is javalang.tree.BinaryOperation:
        return ast.BinaryOperation(node, parent)
    if type(node) is javalang.tree.Literal:
        return ast.Literal(node, parent)
    if type(node) is javalang.tree.TernaryExpression:
        return ast.TernaryExpression(node, parent)
    if type(node) is javalang.tree.Assignment:
        return ast.Assignment(node, parent)
    if type(node) is javalang.tree.SuperMethodInvocation:
        return ast.SuperMethodInvocation(node, parent)
    if type(node) is javalang.tree.ReferenceType:
        return ast.ReferenceType(node, parent)
    if type(node) is javalang.tree.ArrayInitializer:
        return ast.ArrayInitializer(node, parent)
    if type(node) is javalang.tree.BasicType:
        return ast.BasicType(node, parent)
    if type(node) is javalang.tree.ArraySelector:
        return ast.ArraySelector(node, parent)
    print(node)
    assert False # node not implemented


def declaration_method(self):
    # Add scope method
    overloads = findOverload(TaintElt._Class, self.elt.name)
    to_merge = []
    for overload in overloads:
        if not len(overload) == len(self.elt.parameters):
            continue
        ismerge = True
        for type_i in range(len(overload)):
            if overload[type_i] == "None":
                if self.elt.parameters[type_i].type.name in \
                        ["int", "byte", "short", "long", "char", "float",
                         "double", "boolean" ]:
                    ismerge = False
                    break
            elif not overload[type_i] == self.elt.parameters[type_i].type.name:
                ismerge = False
                break
        if ismerge:
            to_merge.append(overload)
    
    nfield = []
    for e in to_merge:
        classes = TaintElt.get(TaintElt._Class, None)
        classe = classes['$' + "|".join(e) + "$$" + self.elt.name]
        for i in range(len(classe["__fields__"][0])):
            if len(nfield) == i:
                nfield.append(classe["__fields__"][0][i])
            else:
                for child in classe["__fields__"][0][i].child_get():
                    nfield[i].child(child)
                for parent in classe["__fields__"][0][i].parent_get():
                    nfield[i].parent(parent)
        del classes['$' + "|".join(e) + "$$" + self.elt.name]
    # Renaming function for overload
    pre = '$'
    # TODO: If type is byte, int or short convert to int
    pre += "|".join(param.type.name for param in self.elt.parameters)
    pre += f'$${self.elt.name}'
    TaintElt.get(TaintElt._Class, None)[pre] = {'__fields__': [nfield]}
    if type(self) is ast.ConstructorDeclaration:
        ret_type = self.elt.name
    else:
        if self.elt.return_type:
            ret_type = self.elt.return_type.name
        else:
            ret_type = "None"
    TaintElt.Class(pre, True, ret_type=ret_type)




def ref_assignment(value, parent):
    # Remove Literral case
    ret = []
    values = [value]
    while len(values) > 0:
        value = values.pop()
        if type(value) is javalang.tree.Literal:
            continue
        if type(value) is javalang.tree.BinaryOperation:
            values.extend([value.operandl, value.operandr])
        path = revxref(JavaLang2NodeAst(value, parent))
        # Reference not found should probably there not in the scope
        if not len(path) == 0:
            ret.append(xref(path[:-1], path[-1]))
            if ret[-1] == None:
                ret.pop()
    return ret

def TypeLiteral(value):
    assert type(value) is str and len(value) > 0
    if value[0] == '"' and value[-1] == '"':
        return "String"
    if value[0] == "'" and value[-1] == "'":
        return "char"
    if value[-1] == 'L':
        return "long"
    if value[-1] == 'f':
        return "float"
    if value[-1] == 'd':
        return "double"
    if value == "null":
        return None
    if value == "true" or value == "false":
        return "boolean"
    return "int"

def findOverload(path, method_name):
    overloads = []
    for k, v in list(TaintElt.get(path, None).items())[1:]:
        if not k[0] == '$':
            continue
        # split types arguments and method
        types, method = k[1:].split('$$')
        if not method == method_name:
            continue
        # split types of arguments
        overloads.append(types.split('|'))
    return overloads

def get_node_typable(n):
    bak_n = n
    found = True
    loop=[]
    while not type(n.node_get()) is ast.LocalVariableDeclaration and \
          not type(n.node_get()) is ast.FieldDeclaration and \
          not type(n.node_get()) is ast.MethodDeclarationParameters and \
          not type(n.node_get()) is ast.ConstructorDeclarationParameters:
        if len(n.parent_get()) <= 0 or n in loop:
            found = False
            break
        loop.append(n)
        n = n.parent_get()[0]
    if found:
        return n
    n = bak_n
    loop=[]
    while not type(n.node_get()) is ast.LocalVariableDeclaration and \
          not type(n.node_get()) is ast.FieldDeclaration and \
          not type(n.node_get()) is ast.MethodDeclarationParameters and \
          not type(n.node_get()) is ast.ConstructorDeclarationParameters:
        assert len(n.child_get()) > 0 or not n in loop
        loop.append(n)
        n = n.child_get()[0]
    return n


def get_types_arguments(arguments, parent):
    types_meth_invok = []
    for argument in arguments:
        if type(argument) is javalang.tree.Literal:
            types_meth_invok.append(TypeLiteral(argument.value))
        else:
            path = revxref(JavaLang2NodeAst(argument, parent), 
                    stop=JavaLang2NodeAst(argument, parent))
            if len(path) == 0:
                types_meth_invok.append("None") # Object but don't know witch one
                continue
            else:
                if type(argument) is javalang.tree.MethodInvocation:
                    pass # TODO find func type
                n = xref(path[:-1], path[-1])
                if n:
                    types_meth_invok.append(get_node_typable(n).node_get().elt.type.name)
                else:
                    types_meth_invok.append("None") # path[0] is the right object
    return types_meth_invok

"""
Convert node given in Type of this node
"""
def conv_type(path : list, node : str, child=False, params_type=None) -> list:
    nodes = TaintElt._nodes
    assert not path is None
    for p in path:
        # Not in scope to analyzed
        if not p in nodes:
            return path
        nodes = nodes[p]
    # If node is already a type return it
    for n in nodes:
        if n[0] == '$':
            n1 = n[1:].split("$$")
            if n1[1] == node:
                if "__type__" in nodes[n]:
                    return [nodes[n]["__type__"]]

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
                        n = get_node_typable(n)
                        return [n.node_get().elt.type.name]
                path = path[:-1]
        else:
            for n in nodes["__fields__"][0]:
                if type(n) is list:
                    continue
                if n.get() == node:
                    n = get_node_typable(n)
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
                                    ast.This,
                                    ast.CastSelectors,
                                    ast.Cast]:
        if type(root[-1].parent) is ast.Cast and not type(root[-1]) is ast.CastSelectors:
            break
        root.append(root[-1].parent)
    return root[-1]

"""
From parent Ast Node to path to access
"""
def revxref(node : ast.BaseNode, stop=None) -> list:
    #print(f"{node.elt}")
    assert node
    prev_type = []
    root = [node]
    last = None
    while len(root) > 0:
        e = root.pop()
        if type(e) is ast.Cast:
            prev_type = [e.elt.type.name]
            if "selectors" in e.elt.__dict__:
                for sel in reversed(e.elt.selectors):
                    root.append(JavaLang2NodeAst(sel, e))
        elif type(e) is ast.MethodInvocation:
            if e.elt.qualifier:
                prev_type = conv_type(prev_type, e.elt.qualifier)
                if prev_type == None: # Log.v 
                    prev_type = [e.elt.qualifier]
                    #return []
                #prev_type.append(e.elt.qualifier)
            if stop:
                if e.elt == stop.elt:
                    prev_type.append(e.elt.member)
                    return prev_type
            tmp_type = conv_type(prev_type, e.elt.member,
                    params_type=get_types_arguments(e.elt.arguments, e))
            if tmp_type:
                prev_type = tmp_type
            else:
                return ["None"]
            if e.elt.selectors:
                for sel in reversed(e.elt.selectors):
                    root.append(JavaLang2NodeAst(sel, e))
        elif type(e) is ast.This:
            if len(prev_type) > 0:
                pass
            elif e.elt.qualifier:
                prev_type = [e.elt.qualifier]
            else:
                prev_type.extend(TaintElt._Class[:-1] if TaintElt._ClassType[-1] else TaintElt._Class)
            for s in reversed(e.elt.selectors):
                if type(s) is javalang.tree.MemberReference:
                    root.append(ast.MemberReference(s, e))
                elif type(s) is javalang.tree.ArraySelector:
                    root.append(ast.ArraySelector(s, e))
                elif type(s) is javalang.tree.MethodInvocation:
                    root.append(ast.MethodInvocation(s, e))
                else:
                    root.append(JavaLang2NodeAst(s, e))
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
            if not tmp:
                return ["None"]
            if tmp[-1] == "List":
                e2 = root.pop()
                if type(e2) is ast.ArraySelector:
                    prev_type = conv_type(prev_type, e.elt.member, child=True)
                else:
                    prev_type = tmp
                    root.append(e2)
        if stop:
            if stop.elt == e.elt:
                break
    if last:
        if last[1] == prev_type:
            return last[0]
    return prev_type

"""
Like xref but give the type at the end and not the name
"""
def get_type(node, nscope=None, stop=None):
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
                # If no prev_type it means the method is not in the scope
                if not prev_type:
                    return []
                #prev_type.append(e.elt.qualifier)
            #prev_type = conv_type(prev_type, e.elt.member)
            tmp_type = conv_type(prev_type, e.elt.member)
            if not tmp_type:
                assert not nscope == None # Scope doesn't exist
                name_scope = "$" + "|".join(str(s) for s in nscope) + "$$" + e.elt.member
                prev_type.append(name_scope)
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
            if tmp[-1] == "List":
                e2 = root.pop()
                if type(e2) is ast.ArraySelector:
                    prev_type = conv_type(prev_type, e.elt.member, child=True)
                else:
                    prev_type = tmp
                    root.append(e2)
            else:
                prev_type = tmp
        if e.elt == stop.elt:
            break

            
            #print(f"{e.elt.qualifier}.{e.elt.member}")
    #print(".".join(prev_type))
    return prev_type

    pass


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
        elt2pos = self._node.elt
        if type(elt2pos) is javalang.tree.Assignment:
            elt2pos = elt2pos.expressionl
        return elt2pos._position if "_position" in elt2pos.__dict__ else ""

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
                        elif type(sc) is Node:
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
        elif type(nodes) is str:
            print("%s%s" % ("\t"* layers, nodes))
        else:
            for k in reversed(nodes):
                #print("%s%s" % ("\t"* layers, ", ".join([str(e) for e in k])))
                print("%s%s" % ("\t"* layers, cls.scope_print(k)))


    @classmethod
    def Class(cls, name, method=False, ret_type=None):
        # Add scope Class
        cls._Class.append(name)
        cls._ClassType.append(method)
        cls.ConstructScope(cls._Class, ret_type=ret_type)

        cls.scope_p.append([-1])

    @classmethod
    def ConstructScope(cls, path, ret_type=None):
        # Traversal graph
        nodes = cls._nodes
        for i in range(len(path) - 1):
            nodes = nodes[path[i]]
        if ret_type:
            nodes[path[-1]]["__type__"] = ret_type
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
    def get(cls, clazz : list, field : str):
        assert type(clazz) is list and (len(clazz) > 0 or field)
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

