
from static.module.register import ModuleStaticCmd

@ModuleStaticCmd("simplify_graph", "Simplify the graph to remove all useless"
                 "node", bool)
class Tree:
    """
    Class Exemple of cresation static module
    """
    def __init__(self, package, tmp_dir, args):
        if args.simplify_graph:
            from . import simplify_graph
        return None

