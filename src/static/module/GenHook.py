
from .register import ModuleStaticCmd

@ModuleStaticCmd("gen_hook", "generate hook", "str", "+")
class GenHook:
    """
    Class Generate Hook

    To use:
      --gen_hook <class>.<func>
    """
    def __init__(self, package, tmp_dir, args):
        if args.gen_hook:
            from . import GenHook_node
            for arg in args.gen_hook:
                hooks = arg.split('.')
                GenHook_node.ClassToHook.add_class(hooks[0])
                GenHook_node.FuncToHook.add_func(hooks[1])
        return None


