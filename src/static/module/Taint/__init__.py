
from static.module.register import ModuleStaticCmd

@ModuleStaticCmd("taint", "taint variable node",
        bool)
class Taint:
    """
    Class Exemple of cresation static module
    """
    def __init__(self, package, tmp_dir, args):
        from . import taint
        return None

