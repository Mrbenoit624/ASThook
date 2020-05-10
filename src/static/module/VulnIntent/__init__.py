
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
        if args.vuln_intent:
            if not "exported" in Output.get_store()["manifest"]["activity"]:
                return
            from . import vuln_intent
            if args.vuln_intent == "poc":
                vuln_intent.poc = True

