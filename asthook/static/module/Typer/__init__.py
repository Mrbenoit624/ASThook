
from asthook.static.module.register import ModuleStaticCmd, load_module

@ModuleStaticCmd("types", "grab type of elements", bool)
class Tree:
    """
    Class Exemple of cresation static module
    """
    def __init__(self, package, tmp_dir, args):
        load_module("Typer", "typer")
        #print("test")
        return None

