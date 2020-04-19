
from .register import ModuleStaticCmd

@ModuleStaticCmd("gen_hook", "generate hook", "str")
class GenHook:
    """
    Class Generate Hook

    To use:
      --gen_hook <class>.<func>
    """
    def __init__(self, package, tmp_dir, args):
        if args.gen_hook:
            from . import GenHook_node
            hooks = args.gen_hook.split('.')
            GenHook_node.ClassToHook.set_class(hooks[0])
            GenHook_node.FuncToHook.set_func(hooks[1])
        return None


