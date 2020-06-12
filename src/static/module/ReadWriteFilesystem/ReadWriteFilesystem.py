from static.ast import Node, ast
from utils import Output
from logging import debug



@Node("ClassCreator", "in")
class ClassCreatorIn:
    @classmethod
    def call(cls, r, self):
        if "android.permission.READ_EXTERNAL_STORAGE" in \
        Output.get_store()["manifest"]["permissions"]["uses"]:
            if "FileInputStream" == self.elt.type.name:
                #debug(f"{r['Filename']}")# : {self.parent.parent.elt._position}")
                Output.add_tree_mod("Filesystem", "READ", f"{r['Filename']}")
        
        if "android.permission.WRITE_EXTERNAL_STORAGE" in \
        Output.get_store()["manifest"]["permissions"]["uses"]:
            if "FileOutputStream" == self.elt.type.name:
                #debug(f"{r['Filename']}")# : {self.parent.parent.elt._position}")
                Output.add_tree_mod("Filesystem", "WRITE", f"{r['Filename']}")
        return r

