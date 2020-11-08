
from asthook.static.module.register import ModuleStaticCmd, load_module
from asthook.utils import Output

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
        load_module("name_file", "name_file_node")
        load_module("Taint", "taint")
        load_module("Provider", "provider")
        
        if args.vuln_intent == "poc":
            provider.poc = True
        

def mprint(arg : list) -> str:
    ret = f"{arg[0]}"
    for i in arg[1]:
        ret+= f"\n\t{i}"
    return ret
