
from .register import ModuleStaticCmd

@ModuleStaticCmd("test", "test", "bool")
class Tree:
    """
    Class Exemple of cresation static module
    """
    def __init__(self, package, tmp_dir, args):
        if args.test:
            from . import name_file_node # dependance
            from . import test_node
        #print("test")
        return None

