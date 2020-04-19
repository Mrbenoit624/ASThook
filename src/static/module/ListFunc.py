
from .register import ModuleStaticCmd

@ModuleStaticCmd("list_funcs", "list all funcs", "str", 2)
class ListFuncs:
    """
    Class List functions
    
    To use:
      --list_funcs '<class>' '<function>'
      with regex for instance to list all functions:
      --list_funcs '.*' '.*'
    """
    def __init__(self, package, tmp_dir, args):
        if args.list_funcs:
            from . import ListFuncs_node
            ListFuncs_node.Class.set_class(args.list_funcs[0])
            ListFuncs_node.Func.set_func(args.list_funcs[1])
        return None


