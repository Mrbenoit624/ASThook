from asthook.static.ast import Node
import re
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

