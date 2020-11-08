
from asthook.static.module.register import ModuleStaticCmd, load_module

@ModuleStaticCmd("taint", "taint variable node",
        bool)
class Taint:
    """
    Class Exemple of cresation static module
    """
    def __init__(self, package, tmp_dir, args):
        load_module("Taint", "taint")
        return None

