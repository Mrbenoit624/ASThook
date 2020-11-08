
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

          load_module("GenHook", "GenHook_node")

          for arg in args.gen_hook:
              hooks = arg.split('.')
              GenHook_node.ClassToHook.add_class(hooks[0])
              GenHook_node.FuncToHook.add_func(hooks[1])
          Output.add_printer_callback("tree", "gen_hook", "hook", mprint)
          return None
          
Function `add_printer_callback` add a custom printer to display your result.
The function given as parameter take as argument a list of object given when
you add a result by the function `add_tree_mod`.

The following code show an exemple of custom print function:

.. code-block:: python

   def mprint(arg : list) -> str:
       pad = "." * (48 - len(arg[0]))
       return f"{arg[0]} {pad} {arg[1]} : {arg[2]}"

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

To add a result to print use function `add_tree_mod` like the following
example:

.. code-block:: python

   @Node("Literal", "in")
   class Literal:
       @classmethod
       def call(cls, r, self):
           self.node_graph.Color = "red"
           for k, names in SeekLiteral.get():
               for name in names:
                   if re.search(name, self.elt.value):
                       self.node_graph.Color = "green"
                       Output.add_tree_mod("seek_literal", k,
                               [self.elt.value,
                               r["Filename"], self.elt._position],
                               r['instance'])
           return r
