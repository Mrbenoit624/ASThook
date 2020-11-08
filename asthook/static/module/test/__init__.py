
from asthook.static.module.register import ModuleStaticCmd, load_module

@ModuleStaticCmd("test", "test", bool)
class Tree:
    """
    Class Exemple of cresation static module
    """
    def __init__(self, package, tmp_dir, args):
        load_module("name_file", "name_file_node")
        load_module("test", "test_node")
        #print("test")
        return None

