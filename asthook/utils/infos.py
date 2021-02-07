import os
import json

class Info_meta(type):

    def __init__(cls, *args, **kwargs):
        cls.__path = None
        cls.__contents = None

    def Init(cls, path):
        cls.__path = f"{path}/info.json"
        cls.__loader()

    def get_path(cls):
        return cls.__path

    def __loader(cls):
        if not os.path.exists(cls.__path):
            cls.__contents = {}
            return
        with open(cls.__path, "r") as f:
            cls.__contents = json.loads(f.read())
        if not cls.__contents:
            cls.__contents = {}

    @property
    def contents(cls):
        if not cls.__contents:
            cls.__loader()
        return cls.__contents

    def get(cls, name):
        if not name in cls.contents:
            return None
        else:
            return cls.__contents[name]

    def set(cls, data, value):
        cls.__contents[data] = value

    def update(cls):
        with open(cls.__path, "w") as f:
            f.write(json.dumps(cls.__contents))


class Info(metaclass=Info_meta):
    pass



