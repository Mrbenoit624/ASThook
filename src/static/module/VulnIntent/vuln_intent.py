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
                r["vuln_intent"][2].append((bool,
                    self.elt.arguments[0].value,
                    r["Filename"] + " : " + str(self.elt._position)))
            elif self.elt.member == "getStringExtra":
                r["vuln_intent"][2].append((str,
                    self.elt.arguments[0].value,
                    r["Filename"] + " : " + str(self.elt._position)))
            elif self.elt.member == "getParcelableExtra":
                r["vuln_intent"][2].append((None,
                    "TODO start Intent forInstance",
                    r["Filename"] + " : " + str(self.elt._position)))
            elif self.elt.member == "getExtras":
                pass
        return r
            

@Node("MethodDeclaration", "out")
class MethodDeclarationOut:
    @classmethod
    def call(cls, r, self):
        if len(r["vuln_intent"][2]) > 0:
            arg = ""
            tmp = []
            for type_, val, pos in r["vuln_intent"][2]:
                if val in tmp:
                    continue
                tmp.append(val)
                if type_ is bool: 
                    arg += " --ez %s true" % val
                elif type_ is str:
                    arg += " --es %s \"<argument>\"" % val
                else:
                    arg += val
            Output.add_tree_mod("vuln_intent", r["vuln_intent"][1], 
            ["\nadb shell 'am start -S -n %s %s'\n" % (
                r["vuln_intent"][0], arg),
                r["vuln_intent"][2]])
        r["vuln_intent"][1] = None
        r["vuln_intent"][2] = []
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
        r["vuln_intent"][2] = []
        return r
