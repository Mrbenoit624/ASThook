
from static.module.register import ModuleStaticCmd
from utils import Output

@ModuleStaticCmd("vuln_intent", "found vuln intent", str)
class Tree:
    """
    Class VulnIntent to found vulnerable intent
    "normal" for nopoc
    "poc" for poc
    """
    def __init__(self, package, tmp_dir, args):
        if not "exported" in Output.get_store()["manifest"]["activity"]:
            return
        from ..name_file import name_file_node
        from . import vuln_intent
        if args.vuln_intent == "poc":
            vuln_intent.poc = True
        

def mprint(arg : list) -> str:
    ret = f"{arg[0]}"
    for i in arg[1]:
        ret+= f"\n\t{i}"
    return ret
