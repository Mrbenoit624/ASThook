ReadJavaFile
============

To get a specific line of a file decompiled by asthook you can use the method:
- ReadJavaFile.readline(<path>, <line>)

This method take the absolute path from the apk `/com/.../file.java` and the
line you want.

For instance you can inspired from this following example:

.. code-block:: python

  from asthook.utils import Output, ReadJavaFile
  
  import asthook.log as logging
  
  @Node("MethodInvocation", "in")
  class MethodInvocation:
      @classmethod
      def call(cls, r, self):
          if self.elt.member == "evaluateJavascript":
              line = ReadJavaFile.readline(r["Filename"], self.elt.position.line)
              Output.add_tree_mod("check_javascript", "evaluateJavascript",
                      [r["Filename"], self.elt._position, line],
                       r['instance'])
          return r
