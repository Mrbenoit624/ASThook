from static.ast import Node

@Node("File", "in")
class File:
    @classmethod
    def call(cls, r, path):
        r["Filename"] = ""
        for i in path.parts[4:]:
            r["Filename"] += "/" + i
        return r
