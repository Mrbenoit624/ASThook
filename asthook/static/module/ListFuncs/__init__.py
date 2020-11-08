
from asthook.static.module.register import ModuleStaticCmd, load_module
from asthook.utils import Output

@ModuleStaticCmd("list_funcs",
        "list all funcs with regex as follow: "
        "--list_funcs <class_regex> <function_regex>",
        str, 2)
class ListFuncs:
    """
    Class List functions
    
    To use:
      --list_funcs '<class>' '<function>'
      with regex for instance to list all functions:
      --list_funcs '.*' '.*'
    """
    def __init__(self, package, tmp_dir, args):
        load_module("ListFuncs", "ListFuncs_node")
        ListFuncs_node.Class.set_class(args.list_funcs[0])
        ListFuncs_node.Func.set_func(args.list_funcs[1])

        Output.add_printer_callback("tree", "list_funcs", "func", mprint)

def mprint(arg : list) -> str:
    pad = "." * (78 - len(arg[0]))
    return f"{arg[0]} {pad} {arg[1]}"


