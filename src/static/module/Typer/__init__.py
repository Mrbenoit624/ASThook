
from static.module.register import ModuleStaticCmd

@ModuleStaticCmd("types", "grab type of elements", bool)
class Tree:
    """
    Class Exemple of cresation static module
    """
    def __init__(self, package, tmp_dir, args):
        from . import typer
        #print("test")
        return None

