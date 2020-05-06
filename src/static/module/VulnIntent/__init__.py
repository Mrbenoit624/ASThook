
from static.module.register import ModuleStaticCmd

@ModuleStaticCmd("vuln_intent", "found vuln intent", bool)
class Tree:
    """
    Class Exemple of creation static module
    """
    def __init__(self, package, tmp_dir, args):
        if args.vuln_intent:
            from . import vuln_intent
            pass
        pass

