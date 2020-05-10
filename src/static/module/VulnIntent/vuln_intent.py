from static.ast import Node
from utils import Output
from static.generate_apk import GenerateAPK, JavaFile
import javalang
import os

poc = False

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
                type_ = None
                name_ = "TODO start Intent forInstance"
                if self.elt.selectors:
                    func = self.elt.selectors[0]
                    if func.member == "getString":
                        type_ = str
                    elif func.member == "getInt":
                        type_ = int
                    if type(func.arguments[0]) is javalang.tree.Literal:
                        name_ = func.arguments[0].value
                r["vuln_intent"][2].append((type_,
                    name_,
                    r["Filename"] + " : " + str(self.elt._position)))
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
                r["vuln_intent"][2],
                r["vuln_intent"][0]])
        r["vuln_intent"][1] = None
        r["vuln_intent"][2] = []
        return r

@Node("ClassDeclaration", "out")
class ClassDeclarationOut:
    @classmethod
    def call(cls, r, self):
        r["vuln_intent"][0] = None
        return r

@Node("Init", "out")
class Init:
    @classmethod
    def call(cls, r, self):
        if poc:
            if not "vuln_intent" in Output.get_store()["tree"]:
                return r
            for k, ps in Output.get_store()["tree"]["vuln_intent"].items():
                for p in ps:
                    appact = p[2].split('/')
                    app = appact[0]
                    activity = appact[1]
                    path = os.path.dirname(__file__) + "/poc/"
                    parameters = []
                    p_ = []
                    tmp = []
                    for i in p[1]:
                        if i[1] in tmp:
                            continue
                        tmp.append(i[1])
                        p_.append([i[0], i[1]])
                    for i in p_:
                        if i[0] is bool:
                            parameters.append({'name' : i[1], 'value' : "true"})
                        elif i[0] is str:
                            parameters.append({'name' : i[1], 'value' : '"Hacked"'})
                        else:
                            parameters.append({'name' : '"TODO"', 'value' : '"TODO"'})
                    manifest = JavaFile("/AndroidManifest.xml",
                            path + "AndroidManifest.xml",
                            {'app' : app,
                             'activity' : activity})
                    exploit = JavaFile("/exploit/intent/exploit.java",
                            path + "/java/exploit/intent/exploit.java",
                            {'app' : app,
                             'activity' : activity,
                             'parameters' : parameters})
                    GenerateAPK("vulnIntent_%s" % activity,
                            manifest,
                            [exploit],
                            self.args, self.get_tmp())
        return r

@Node("Init", "in")
class Init:
    @classmethod
    def call(cls, r, self):
        r["vuln_intent"] = [None] * 3
        r["vuln_intent"][2] = []
        return r

