
from static.module.register import ModuleStaticCmd

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
        if args.list_funcs_call:
            from ..name_file import name_file_node # dependance
            from ..Typer import typer
            from . import ListFuncsCalled_node
            ListFuncsCalled_node.Class.set_class(args.list_funcs_call[0])
            ListFuncsCalled_node.Func.set_func(args.list_funcs_call[1])
        return None


