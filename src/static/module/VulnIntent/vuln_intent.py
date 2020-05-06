from static.ast import Node
from utils import Output

@Node("ClassDeclaration", "in")
class ClassDeclarationIn:
    @classmethod
    def call(cls, r, self):
        activity = r["package"] + "." + self.elt.name
        if activity in Output.get_store()["manifest"]["activity"]["exported"]:
            r["vuln_intent"][0] = r["package"] + "/" + r["package"] + "." + self.elt.name
        return r

@Node("MethodDeclaration", "in")
class MethodDeclarationIn:
    @classmethod
    def call(cls, r, self):
        activites_status = ["onCreate", "onStart", "onResume", "onPause",
        "onStop", "onRestart", "onDestroy"]
        if self.elt.name in activites_status:
            r["vuln_intent"][1] = self.elt.name
        return r

@Node("MethodInvocation", "in")
class MethodInvocationIn:
    @classmethod
    def call(cls, r, self):
        if r["vuln_intent"][0] and \
                r["vuln_intent"][1]:
            if self.elt.member == "getBooleanExtra":
                r["vuln_intent"][2] = " --ez %s true" % self.elt.arguments[0].value
            elif self.elt.member == "getStringExtra":
                r["vuln_intent"][2] = "-e %s <argument>" % self.elt.arguments[0].value
            elif self.elt.member == "getParcelableExtra":
                r["vuln_intent"][2] = "TODO start Intent forInstance"
            elif self.elt.member == "getExtras":
                pass
        return r
            

@Node("MethodDeclaration", "out")
class MethodDeclarationOut:
    @classmethod
    def call(cls, r, self):
        if r["vuln_intent"][2]:
            Output.add_tree_mod("vuln_intent", r["vuln_intent"][1], 
            "adb shell am start -S -n %s %s" % (
                r["vuln_intent"][0], r["vuln_intent"][2]))
        r["vuln_intent"][1] = None
        r["vuln_intent"][2] = None
        return r

@Node("ClassDeclaration", "out")
class ClassDeclarationOut:
    @classmethod
    def call(cls, r, self):
        r["vuln_intent"][0] = None
        return r

@Node("File", "in")
class File:
    @classmethod
    def call(cls, r, path):
        return r

@Node("Init", "in")
class Init:
    @classmethod
    def call(cls, r):
        r["vuln_intent"] = [None] * 3
        return r
