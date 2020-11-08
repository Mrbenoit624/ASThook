from asthook.static.module.register import ModuleStaticCmd, load_module
from asthook.utils import *

@ModuleStaticCmd("user_input", "list all users input", bool)
class ListUserInput:
    """
    Class List all user Input

    To use:
      --user_input
    """
    def __init__(self, package, tmp_dir, args):
        load_module("name_file", "name_file_node")
        load_module("ListUserInput", "ListUserInput_node")
        Output.add_printer_callback("tree", "user_input", "EditText/TextView", mprint)

def mprint(arg : list) -> str:
    return f"{warning(arg[0])} {arg[1]} {arg[2]}"
