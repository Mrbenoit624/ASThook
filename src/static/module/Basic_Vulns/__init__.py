
from static.module.register import ModuleStaticCmd

@ModuleStaticCmd("basic_vulns", "seek several potentials vulns",
        bool)
class NameFile:
    """
    Class Exemple of cresation static module
    """
    def __init__(self, package, tmp_dir, args):
        from . import basic_vulns
        from ..name_file import name_file_node
        return None

