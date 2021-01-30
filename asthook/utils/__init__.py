from contextlib import contextmanager
from sty import fg, bg, ef, rs, Style, RgbFg
import sys
import signal
import json
import re
from asthook import log as logging


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
        cls.store = [{"manifest": {},
                      "tree"    : {},
                      "dynamic" : {}
                    }]
        #cls.store[0]["manifest"] = {}
        #cls.store[0]["tree"] = {}
        #cls.store[0]["dynamic"] = {}
        cls.printer_callback = cls.store.copy()
        cls.store_restore = cls.store.copy()
        #cls.printer_callback = {"manifest": {},
        #                        "tree": {}}
        #cls.store_restore = [{"manifest": {},
        #                        "tree": {}}]

    @classmethod
    def replace(cls, store, instance=0):
        if len(cls.store) <= instance:
            cls.store.append(store)
        cls.store[instance] = store

    @classmethod
    def load(cls, restore_outputs):
        for restore_output in restore_outputs:
            with open(restore_output) as f:
                cls.store[0].update(json.loads(f.read()))
        cls.store_restore[0] = cls.store[0]

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
        if not module in cls.store_restore[0][category]:
            return False
        if not tag in cls.store_restore[0][category][module]:
            return False
        return arg in cls.store_restore[0][category][module][tag]

    @classmethod
    def browse_to_store(cls, category, module, tag, instance=0):
        if not module in cls.store[instance][category]:
            cls.store[instance][category][module] = {}
        if not tag in cls.store[instance][category][module]:
            cls.store[instance][category][module][tag] = []
        return cls.store[instance][category][module][tag]

    @classmethod
    def add_to_store(cls, category, module, tag, arg, instance=0):
        cls.browse_to_store(category, module, tag, instance).append(arg)

    @classmethod
    def get_to_store(cls, category, module, tag, instance=0):
        return cls.browse_to_store(category, module, tag, instance)

    @classmethod
    def add_tree_mod(cls, module, tag, arg, instance=0):
        cls.add_to_store("tree", module, tag, arg, instance)

    @classmethod
    def add_dynamic_mod(cls, module, tag, arg, instance=0):
        cls.add_to_store("dynamic", module, tag, arg, instance)

    @classmethod
    def get_dynamic_mod(cls, module, tag, instance=0):
        return cls.get_to_store("dynamic", module, tag, instance)


    @classmethod
    def get_store(cls, instance=0):
        return cls.store[instance]

    @classmethod
    def none_print(cls, instance=0):
        ret = ""
        for modulek, modulev in cls.store[instance]["tree"].items():
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
    def print_static_module(cls, instance=0):
        print(cls.none_print(instance))

    @classmethod
    def dump(cls, mode, instance=0):
        if mode == "json":
            return json.dumps(cls.store[instance], sort_keys=True,
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



