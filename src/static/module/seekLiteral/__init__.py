
from static.module.register import ModuleStaticCmd

@ModuleStaticCmd("seek_literal", "seek Literal specify wit regexp", str, "+")
class SeekLiteral:
    """
    Class Exemple of creation static module
    """
    def __init__(self, package, tmp_dir, args):
        from ..name_file import name_file_node
        from . import seek_literal
        seek_literal.SeekLiteral.add("personal", args.seek_literal)
        return None

