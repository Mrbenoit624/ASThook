from static.ast import Node

@Node("ClassDeclaration", "in")
class Toto:
    @classmethod
    def call(cls, r, self):
        r["toto"] = r["toto"] + 1
        print("%s%s%d\t%s%s:%s" % (self.elt.name," "*(47-len(self.elt.name)),
                                  r["toto"], r["Filename"],
                                  " " * (55-len(r["Filename"])), self.elt._position))
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
