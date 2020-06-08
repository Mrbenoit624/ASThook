
from static.module.register import ModuleStaticCmd
from utils import Output
from sty import fg, bg, ef, rs, Style, RgbFg

@ModuleStaticCmd("basic_vulns", "seek several potentials vulns",
        bool)
class NameFile:
    """
    Class Exemple of cresation static module
    """
    def __init__(self, package, tmp_dir, args):
        from . import basic_vulns
        from ..name_file import name_file_node
        Output.add_printer_callback("tree", "basic_vulns", "Unsecure Random",
                UnsecureRandomPrint)
        return None

def UnsecureRandomPrint(arg : list) -> str:
    return f"Unsecure random on {ef.b}{arg}{rs.all}\n" \
            "\tTo crack this random you can use " \
            "https://jazzy.id.au/2010/09/20/cracking_random_number_generators_part_1.html\n" \
            "\tIt better to use java.security.SecureRandom to avoid " \
            "to predict the next random number"

