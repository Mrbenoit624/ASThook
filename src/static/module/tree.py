
from .register import ModuleStaticCmd

@ModuleStaticCmd("test", "test")
class Tree:
    """
    Class Exemple of cresation static module
    """
    def __init__(self, package, tmp_dir, args):
        if args.test:
            from . import tree_node
        #print("test")
        return None

