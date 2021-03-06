from asthook.static.ast import Node
import re
from asthook.utils import Output

@Node("Literal", "in")
class Literal:
    @classmethod
    def call(cls, r, self):
        self.node_graph.Color = "red"
        for k, names in SeekLiteral.get():
            for name in names:
                if re.search(name, self.elt.value):
                    self.node_graph.Color = "green"
                    Output.add_tree_mod("seek_literal", k,
                            [self.elt.value,
                            r["Filename"], self.elt._position],
                            r['instance'])
        return r

class SeekLiteral:

    @classmethod
    def add(cls, from_, args):
        if not "names" in cls.__dict__:
            cls.names = {}
        if not from_ in cls.names.keys():
            cls.names[from_] = []
        cls.names[from_].extend(args)

    @classmethod
    def get(cls):
        return cls.names.items()
