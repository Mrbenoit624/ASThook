from ..ast import Node

@Node("ClassDeclaration", "in")
class Toto:
    @classmethod
    def call(cls, r, self):
        r["toto"] = r["toto"] + 1
        print("test %d %s" % (r["toto"], r["todo"]))
        return r

@Node("File", "in")
class File:
    @classmethod
    def call(cls, r, path):
        r["toto"] = 0
        r["todo"] = path
        return r

@Node("Init", "in")
class Init:
    @classmethod
    def call(cls, r):
        r["toto"] = 0
        return r
