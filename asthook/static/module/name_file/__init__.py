
from asthook.static.module.register import ModuleStaticCmd, load_module

@ModuleStaticCmd("name_file", "store the name of the file to be accessible by Node",
        bool)
class NameFile:
    """
    Class Exemple of cresation static module
    """
    def __init__(self, package, tmp_dir, args):
        load_module("name_file", "name_file_node")
        return None

