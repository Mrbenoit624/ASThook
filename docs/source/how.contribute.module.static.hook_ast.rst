
Hook AST
========


Hook AST is a module allow user to hook each nodes of the ast and inspect the
content.

To load this module you should write each hook on a file not load automaically
and load it manually only when the plugin is loaded like the following example:

.. code-block:: python

  @ModuleStaticCmd("gen_hook", "generate hook", str, "+")
  class GenHook:
      """
      Class Generate Hook

      To use:
        --gen_hook <class>.<func>
      """
      def __init__(self, package, tmp_dir, args):
          from . import GenHook_node
          for arg in args.gen_hook:
              hooks = arg.split('.')
              GenHook_node.ClassToHook.add_class(hooks[0])
              GenHook_node.FuncToHook.add_func(hooks[1])
          Output.add_printer_callback("tree", "gen_hook", "hook", mprint)
          return None 

To hook a node you should use a decorator like the following example:

.. code-block:: python

  @Node("ClassDeclaration", "in")
   class ClassDeclaration:
       @classmethod
       def call(cls, r, self):
           for i in range(0, len(r["gen_hook_class"])):
               if self.elt.name == ClassToHook.get_name()[i]:
                   r["gen_hook_class"][i] = True
           return r
