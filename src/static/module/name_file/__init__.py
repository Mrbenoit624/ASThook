
from static.module.register import ModuleStaticCmd

@ModuleStaticCmd("name_file", "store the name of the file to be accessible by Node",
        bool)
class NameFile:
    """
    Class Exemple of cresation static module
    """
    def __init__(self, package, tmp_dir, args):
        from . import name_file_node
        return None

