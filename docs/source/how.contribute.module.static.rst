Make a Static module
====================

.. code-block:: python

  from static.module.register import ModuleStaticCmd

  from utils import Output
  
  @ModuleStaticCmd("seek_literal", "seek Literal specify with regexp", str, "+")
  class SeekLiteral:
      """
      Class Exemple of creation static module
      """
      def __init__(self, package, tmp_dir, args):
          from ..name_file import name_file_node
          from . import seek_literal
  
          seek_literal.SeekLiteral.add("personal", args.seek_literal)
  
          Output.add_printer_callback("tree", "seek_literal", "personal", mprint)
  
  def mprint(arg : list) -> str:
      pad = "." * (48 - len(arg[0]))
      return f"{arg[0]} {pad} {arg[1]} : {arg[2]}"

The constructor of the class give access to:

- package: name of the package to analyse
- tmp_dir str: to give the path where all files of this project is store
- args object: to give all arguments give by user at launch or on the
  interactive mode.

You need to create a class with the decorator appropriate

.. toctree::
  :maxdepth: 1
  :titlesonly:
  :glob:

  how.contribute.module.static.*
