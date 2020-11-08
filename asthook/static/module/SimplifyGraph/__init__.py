
from asthook.static.module.register import ModuleStaticCmd, load_module

@ModuleStaticCmd("simplify_graph", "Simplify the graph to remove all useless"
                 "node", bool)
class Tree:
    """
    Class Exemple of cresation static module
    """
    def __init__(self, package, tmp_dir, args):
        load_module("SimplifyGraph", "simplify_graph")
        return None

