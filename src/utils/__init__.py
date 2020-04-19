from contextlib import contextmanager
from sty import fg, bg, ef, rs, Style, RgbFg
import sys
import signal

fg.orange = Style(RgbFg(255, 150, 50))
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

