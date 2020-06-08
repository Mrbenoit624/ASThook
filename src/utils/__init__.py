from contextlib import contextmanager
from sty import fg, bg, ef, rs, Style, RgbFg
import sys
import signal
import json
import re


fg.orange = Style(RgbFg(255, 150, 50))
fg.grey = Style(RgbFg(150, 150, 150))
fg.blue = Style(RgbFg(54,154,205))
fg.h2 = Style(RgbFg(30,196,220))
if not sys.stdout.isatty():
    fg.orange = ""
    fg.li_blue = ""
    fg.li_yellow = ""
    fg.li_red = ""
    fg.grey = ""
    fg.li_green = ""
    fg.rs = ""

def bprint(text):
    """
    Create a beautiful print
    """
    size = int(len(text)/2)
    print()
    print(fg.li_blue + "#" * 80 + fg.rs)
    print("%s%s" % (" " * (40 - size), text))
    print(fg.li_blue + "#" * 80 + fg.rs, end='\n\n')

def h2(text):
    """
    Create a beautiful print
    """
    size = int(len(text)/2)
    print()
    print("%s %s %s\n" % (fg.blue + "*" * (39 - size) + fg.rs,
        fg.h2 + text,
        fg.blue + "*" * (39 - size) + fg.rs))

def warning(elt):
    return fg.orange + elt + fg.rs

def info(elt):
    return fg.li_yellow + elt + fg.rs

def error(elt):
    return fg.li_red + elt + fg.rs

def good(elt):
    return fg.li_green + elt + fg.rs

def hide(elt):
    return fg.grey + elt + fg.rs


@contextmanager
def timeout(time):
    """
    Timeout for avoid eternal loop function
    """
    signal.signal(signal.SIGALRM, raise_timeout)
    signal.alarm(time)

    try:
        yield
    except TimeoutError:
        pass
    finally:
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError

class Output:

    @classmethod
    def init(cls):
        cls.store = {}
        cls.store_td = {}
        cls.store["manifest"] = {}
        cls.store["tree"] = {}
        #cls.store["dynamic"] = {}
        cls.store_td["manifest"] = {}
        cls.store_td["tree"] = {}
        #cls.store_td["dynamic"] = {}
        cls.printer_callback = {"manifest": {},
                                "tree": {}}

    @classmethod
    def add_printer_callback(cls, category, module, tag, func):
        if not module in cls.printer_callback[category]:
            cls.printer_callback[category][module] = {}
        cls.printer_callback[category][module][tag] = func

    @classmethod
    def get_printer_callback(cls, category, module, tag):
        if not module in cls.printer_callback[category]:
            return None
        if not tag in cls.printer_callback[category][module]:
            return None
        return cls.printer_callback[category][module][tag]


    @classmethod
    def add_to_store(cls, category, module, tag, arg):
        if not module in cls.store[category]:
            cls.store[category][module] = {}
            cls.store_td[category][module] = {}
        if not tag in cls.store[category][module]:
            cls.store[category][module][tag] = []
            cls.store_td[category][module][tag] = []
        cls.store[category][module][tag].append(arg)
        if type(arg) is str:
            cls.store_td[category][module][tag].append(re.sub("\\u001b\[.*?m", "", arg))
        elif type(arg) is dict:
            tmp = {}
            for k, v in arg.items():
                if type(v) is str:
                    tmp[k] = re.sub("\\u001b\[.*?m", "", v)
                else:
                    tmp[k] = v
            cls.store_td[category][module][tag].append(tmp)
        else:
            tmp = []
            for e in arg:
                if type(e) is str:
                    tmp.append(re.sub("\\u001b\[.*?m", "", e))
                else:
                    tmp.append(e)
            cls.store_td[category][module][tag].append(tmp)

    @classmethod
    def add_tree_mod(cls, module, tag, arg):
        cls.add_to_store("tree", module, tag, arg)


    @classmethod
    def get_store(cls):
        return cls.store_td

    @classmethod
    def none_print(cls):
        ret = ""
        for modulek, modulev in cls.store["tree"].items():
            for tagk, tagv in modulev.items():
                call = cls.get_printer_callback("tree", modulek, tagk)
                if not call:
                    continue
                for arg in tagv:
                    ret += "[ %s ] [ %s ] " % (
                        fg.li_cyan + modulek + fg.rs,
                        fg.li_magenta + tagk + fg.rs)
                    ret += call(arg)
                    ret += '\n'
        return ret

    @classmethod
    def print_static_module(cls):
        print(cls.none_print())

    @classmethod
    def dump(cls, mode):
        if mode == "json":
            return json.dumps(cls.store_td, sort_keys=True,
                    indent=4,cls=cls.SpecialEncoder)
        elif mode == "none":
            return cls.none_print()

    class SpecialEncoder(json.JSONEncoder):
        def default(self, o):
            if type(o) is type:
                return str(o)
            return json.JSONEncoder.default(self, o)
        
        def py_encode_basestring(self, s):
            return s



