
from asthook.static.module.register import ModuleStaticCmd, load_module

from asthook.utils import Output

@ModuleStaticCmd("check_javascript", "check js called", bool)
class CheckJavascript:
    """
    Class Exemple of creation static module
    """
    def __init__(self, package, tmp_dir, args):
        load_module("name_file", "name_file_node")
        load_module("CheckJavascript", "check_javascript")

        Output.add_printer_callback("tree", "check_javascript",
                "evaluateJavascript", mprint)

def mprint(arg : list) -> str:
    return f"{arg[0]} : {arg[1]}\n                                            {arg[2]}"


