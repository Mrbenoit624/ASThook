
from asthook.static.module.register import ModuleStaticCmd, load_module
from asthook.utils import Output

@ModuleStaticCmd("list_funcs_call",
        "list all funcs called with regex as follow: "
        "--list_funcs_call <class_regex> <function_regex>",
        str, 2)
class ListFuncs:
    """
    Class List functions

    To use:
      --list_funcs_call '<class>' '<function>'
      with regex for instance to list all functions:
      --list_funcs_call '.*' '.*'
    """
    def __init__(self, package, tmp_dir, args):
        load_module("name_file", "name_file_node")
        load_module("Typer", "typer")
        load_module("ListFuncsCall", "ListFuncsCalled_node")

        if args.taint:
            ListFuncsCalled_node.with_taint()
        ListFuncsCalled_node.Class.set_class(args.list_funcs_call[0])
        ListFuncsCalled_node.Func.set_func(args.list_funcs_call[1])

        Output.add_printer_callback("tree", "list_funcs_called", "func", mprint)


def mprint(arg : list) -> str:
    pad = "." * (38 - len(arg[0]))
    return f"{arg[0]} {pad} {arg[1]} {arg[2]}"
