from contextlib import contextmanager
from sty import fg, bg, ef, rs, Style, RgbFg
import sys
import signal
import json
import re

fg.orange = Style(RgbFg(255, 150, 50))
fg.blue = Style(RgbFg(54,154,205))
fg.h2 = Style(RgbFg(30,196,220))
if not sys.stdout.isatty():
    fg.orange = ""
    fg.li_blue = ""
    fg.li_yellow = ""
    fg.li_red = ""
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
    
    @classmethod
    def add_to_store(cls, category, module, tag, arg):
        if not module in cls.store[category]:
            cls.store[category][module] = {}
            cls.store_td[category][module] = {}
        if not tag in cls.store[category][module]:
            cls.store[category][module][tag] = []
            cls.store_td[category][module][tag] = []
        cls.store[category][module][tag].append(arg)
        if not type(arg) is list:
            cls.store_td[category][module][tag].append(re.sub("\\u001b\[.*?m", "", arg))
        else:
            cls.store_td[category][module][tag].append([re.sub("\\u001b\[.*?m", "", e)
                for e in arg])

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
                for arg in tagv:
                    if type(arg) is list:
                        ret += "[ %s ] [ %s ]  " % (
                            fg.li_cyan + modulek + fg.rs,
                            fg.li_magenta + tagk + fg.rs)
                        for i in arg:
                            ret += i + "\t"
                        ret += '\n'
                    else:
                        ret += "[ %s ] [ %s ]  %s" % (
                            fg.li_cyan + modulek + fg.rs,
                            fg.li_magenta + tagk + fg.rs,
                            arg) + "\n"
        return ret


    @classmethod
    def print_static_module(cls):
        print(cls.none_print())

    @classmethod
    def dump(cls, mode):
        if mode == "json":
            return json.dumps(cls.store_td, sort_keys=True, indent=4)
        elif mode == "none":
            return cls.none_print()





