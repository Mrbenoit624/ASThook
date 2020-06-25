from contextlib import contextmanager
from sty import fg, bg, ef, rs, Style, RgbFg
import sys
import signal
import json
import re
import log as logging


import subprocess


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

class extcall:
    @classmethod
    def external_call(cls, call):
        if not "prevout" in cls.__dict__:
            cls.prevout = ""
            cls.preverr = ""
        p = subprocess.Popen(call, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        out, err = p.communicate()
        if not cls.prevout == out and len(out) > 0:
            cls.prevout = out
            for o in out.decode().split('\n'):
                if len(o) > 0:
                    logging.info(o)
        if not cls.preverr == err and len(err) > 0:
            cls.preverr = err
            for o in err.decode().split('\n'):
                if len(o) > 0:
                    logging.warning(o)
        return p.returncode

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
        cls.store["manifest"] = {}
        cls.store["tree"] = {}
        #cls.store["dynamic"] = {}
        cls.printer_callback = {"manifest": {},
                                "tree": {}}
        cls.store_restore = {"manifest": {},
                                "tree": {}}

    @classmethod
    def load(cls, restore_outputs):
        for restore_output in restore_outputs:
            with open(restore_output) as f:
                cls.store.update(json.loads(f.read()))
        cls.store_restore = cls.store

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
    def in_restore(cls, category, module, tag, arg):
        if not module in cls.store_restore[category]:
            return False
        if not tag in cls.store_restore[category][module]:
            return False
        return arg in cls.store_restore[category][module][tag]

    @classmethod
    def add_to_store(cls, category, module, tag, arg):
        if not module in cls.store[category]:
            cls.store[category][module] = {}
        if not tag in cls.store[category][module]:
            cls.store[category][module][tag] = []
        if not cls.in_restore(category, module, tag, arg):
            cls.store[category][module][tag].append(arg)

    @classmethod
    def add_tree_mod(cls, module, tag, arg):
        cls.add_to_store("tree", module, tag, arg)


    @classmethod
    def get_store(cls):
        return cls.store

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
            return json.dumps(cls.store, sort_keys=True,
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



