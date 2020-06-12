
from static.module.register import ModuleStaticCmd
from utils import Output

@ModuleStaticCmd("provider", "analyse provider", str)
class Tree:
    """
    Analyse provider
    """
    def __init__(self, package, tmp_dir, args):

        if not "provider" in Output.get_store()["manifest"] or \
                not "exported" in Output.get_store()["manifest"]["provider"]:
                    return
        #if not "exported" in Output.get_store()["manifest"]["activity"]:
        #    return
        from ..name_file import name_file_node
        from ..Taint import taint
        from . import provider
        if args.vuln_intent == "poc":
            provider.poc = True
        

def mprint(arg : list) -> str:
    ret = f"{arg[0]}"
    for i in arg[1]:
        ret+= f"\n\t{i}"
    return ret
