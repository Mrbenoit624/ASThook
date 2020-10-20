from static.ast import Node
from utils import Output
from static.generate_apk import GenerateAPK, JavaFile
import javalang
import os

from . import mprint

class long:
    pass

class long_a:
    pass

class bytes_a:
    pass

class int_a:
    pass

class float_a:
    pass

poc = False

@Node("ClassDeclaration", "in")
class ClassDeclarationIn:
    @classmethod
    def call(cls, r, self):
        #### get Activity name as written in manifest ####
        activity = r["package"] + "." + self.elt.name
        if activity in Output.get_store()["manifest"]["activity"]["exported"]:
            package = Output.get_store()['manifest']['activity']['package'][0]
            r["vuln_intent"][0] = package + "/" + r["package"] + "." + self.elt.name
        return r

@Node("MethodDeclaration", "in")
class MethodDeclarationIn:
    @classmethod
    def call(cls, r, self):
        activites_status = ["onCreate", "onStart", "onResume", "onPause",
        "onStop", "onRestart", "onDestroy"]
        #if self.elt.name in activites_status:
        #    r["vuln_intent"][1] = self.elt.name
        r["vuln_intent"][1] = self.elt.name
        return r

def DataDetect(elt, parent):
    return elt.member == "getDataString" or elt.member == "getData"

def ExtraDetect(elt, parent):
    if elt.member == "getBooleanExtra":
        return (bool, elt.arguments[0].value)
    elif elt.member == "getStringExtra":
        return (str, elt.arguments[0].value)
    elif elt.member == "getIntExtra":
        return (int, elt.arguments[0].value)
    elif elt.member == "getLongExtra":
        return (long, elt.arguments[0].value)
    elif elt.member == "getFloatExtra":
        return (float, elt.arguments[0].value)
    elif elt.member == "getIntArrayExtra":
        return (int_a, elt.arguments[0].value)
    elif elt.member == "getLongArrayExtra":
        return (long_a, elt.arguments[0].value)
    elif elt.member == "getFloatArrayExtra":
        return (float_a, elt.arguments[0].value)
    elif elt.member == "getByteArrayExtra":
        return (bytes_a, elt.arguments[0].value)
    elif elt.member == "getParcelableExtra":
        return (None, "TODO Parcelable")
    elif elt.member == "getExtras":
       type_ = None
       name_ = "TODO"
       func = None
       if elt.selectors:
           func = elt.selectors[0]
       elif "selectors" in parent.elt and parent.elt.selectors:
           i = parent.elt.selectors.index(self.elt)
           if i + 1 < len(parent.elt.selectors):
               func = parent.elt.selectors[i+1]
       if func:
           if func.member == "getString":
               type_ = str
           elif func.member == "getInt":
               type_ = int
           if type(func.arguments[0]) is javalang.tree.Literal:
               name_ = func.arguments[0].value
       return (type_, name_)
    return (None, None)

def AdbArgs_extra(elts):
    arg = ""
    tmp = []
    for type_, val, pos in elts:
        if val in tmp:
            continue
        tmp.append(val)
        if type_ is bool: 
            arg += " --ez %s true" % val
        elif type_ is str:
            arg += " --es %s \"<argument>\"" % val
        elif type_ is int:
            arg += " --ei %s 1" % val
        elif type_ is long:
            arg += " --el %s 1" % val
        elif type_ is float:
            arg += " --ef %s 1.0" % val
        elif type_ is int_a:
            arg += " --eia %s 1,1" % val
        elif type_ is long_a:
            arg += " --ela %s 1,1" % val
        elif type_ is float_a:
            arg += " --efa %s 1.0,1.0" % val
        elif type_ is bytes_a:
            arg += " --eba %s 1,1" % val
        else:
            pass
    return arg


@Node("MethodInvocation", "in")
class MethodInvocationIn:
    @classmethod
    def call(cls, r, self):
        if r["vuln_intent"][0] and \
                r["vuln_intent"][1]:
            type_, value = ExtraDetect(self.elt, self.parent)
            if value:
                r["vuln_intent"][2].append((type_,
                    value,
                    r["Filename"] + " : " + str(self.elt._position)))
            elif DataDetect(self.elt, self.parent):
                r["vuln_intent"][2].append((self.elt.member,"Deeplink",
                    r["Filename"] + " : " + str(self.elt._position)))
            elif self.elt.member == "setClipData":
                r["vuln_intent"][2].append((self.elt.member,"Deeplinks",
                    r["Filename"] + " : " + str(self.elt._position)))

        return r


@Node("MethodDeclaration", "out")
class MethodDeclarationOut:
    @classmethod
    def call(cls, r, self):
        if len(r["vuln_intent"][2]) > 0:
            arg = AdbArgs_extra(r["vuln_intent"][2])
            Output.add_printer_callback("tree", "vuln_intent", r["vuln_intent"][1], mprint)
            Output.add_tree_mod("vuln_intent", r["vuln_intent"][1], 
            ["adb shell 'am start -S -n %s %s'" % (
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
                    #app = Output.get_store()['manifest']['activity']['package'][0]
                    app = appact[0]
                    activity = appact[1]
                    path = os.path.dirname(__file__) + "/poc/"
                    parameters = []
                    Data = ""
                    Datas = ""
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
                        elif i[0] is int or i[0] is float or i[0] is long:
                            parameters.append({'name' : i[1], 'value' : "1"})
                        elif i[0] is int_a or i[0] is float_a or i[0] is long_a:
                            parameters.append({'name' : i[1], 'value' : "[1, 1]"})
                        elif i[1] == "Deeplink":
                            acti = Output.get_store()["manifest"]["deeplink"][activity][0]
                            Data = "%s://%s%s" % (
                                "" if len(acti["scheme"]) < 1 else acti["scheme"][0],
                                "" if len(acti["host"]) < 1 else acti["host"][0],
                                "" if len(acti["pathPrefix"]) < 1 else acti["pathPrefix"][0]
                                )
                        elif i[1] == "Deeplinks":
                            acti = Output.get_store()["manifest"]["deeplink"][activity][0]
                            Datas = "%s://%s%s" % (
                                "" if len(acti["scheme"]) < 1 else acti["scheme"][0],
                                "" if len(acti["host"]) < 1 else acti["host"][0],
                                "" if len(acti["pathPrefix"]) < 1 else acti["pathPrefix"][0]
                                )
                            #print("%s%s%s" % (str(acti["scheme"]),
                            #    str(acti["host"]),
                            #    str(acti["pathPrefix"])))
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
                             'parameters' : parameters,
                             'data': Data,
                             'datas': Datas})
                    GenerateAPK("vulnIntent_%s_%s" % (activity, k),
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

