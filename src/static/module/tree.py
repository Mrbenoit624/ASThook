
from .register import ModuleStaticCmd
from ..ast import Node

@ModuleStaticCmd("test", "test")
class Tree:
    def __init__(self, package, tmp_dir, args):
        #print("test")
        return None

@Node("ClassDeclaration")
class Toto:
    @classmethod
    def call(cls, r, self):
        r["toto"] = r["toto"] + 1
        print("test %d %s" % (r["toto"], r["todo"]))
        return r

@Node("File")
class File:
    @classmethod
    def call(cls, r, path):
        r["toto"] = 0
        r["todo"] = path
        return r

@Node("Init")
class Init:
    @classmethod
    def call(cls, r):
        r["toto"] = 0
        return r
