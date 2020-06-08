
from static.module.register import ModuleStaticCmd
from utils import Output

@ModuleStaticCmd("gen_hook", "generate hook", str, "+")
class GenHook:
    """
    Class Generate Hook

    To use:
      --gen_hook <class>.<func>
    """
    def __init__(self, package, tmp_dir, args):
        from . import GenHook_node
        for arg in args.gen_hook:
            hooks = arg.split('.')
            GenHook_node.ClassToHook.add_class(hooks[0])
            GenHook_node.FuncToHook.add_func(hooks[1])
        Output.add_printer_callback("tree", "gen_hook", "hook", mprint)
        return None

def mprint(arg : list) -> str:
    return f"{arg[0]}\n{arg[1]}"
