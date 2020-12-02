from asthook.static.ast import Node
from asthook import conf
from pathlib import Path

@Node("File", "in")
class File:
    @classmethod
    def call(cls, r, path):
        r["Filename"] = ""
        size_origine_path = len(Path(conf.DIR).parts) - 1
        for i in path.parts[size_origine_path + 4:]:
            r["Filename"] += "/" + i
        return r
