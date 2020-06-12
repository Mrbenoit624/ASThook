import os
import sys
import logging
from pathlib import Path

from sty import fg, bg, ef, rs, Style, RgbFg
from utils import bprint, warning, info, error, good

from static import StaticAnalysis
from dynamic import DynamicAnalysis
from config import Config
import parser
from utils import Output

DIR="temp"

fg.blue = Style(RgbFg(54,154,205))
class MyFormatter(logging.Formatter):

    def __init__(self, position):
        super().__init__(fmt="%(levelno)d: %(msg)s", datefmt=None, style='%')  
        if position:
            self.position = warning("[ %(pathname)s : %(lineno)s ]")
        else:
            self.position = ""

        base = fg.cyan + " [%(asctime)s]" + fg.rs +" %(msg)s"
        self.err_fmt  = error("[!]") + self.position + base
        self.warn_fmt = warning("[-]") + base
        self.dbg_fmt  = good("[?]") + self.position + " %(msg)s"
        self.info_fmt = info("[*]") + base

    def format(self, record):

        format_orig = self._style._fmt

        npath = Path(__file__).parent.absolute()
        
        if str(record.pathname).startswith(str(npath)):
            record.pathname = Path(record.pathname).relative_to(npath)
        else:
            self._style._fmt = format_orig
            return "" #logging.Formatter.format(self, record)
        if record.levelno == logging.DEBUG:
            self._style._fmt = self.dbg_fmt
        elif record.levelno == logging.INFO:
            self._style._fmt = self.info_fmt
        elif record.levelno == logging.ERROR:
            self._style._fmt = self.err_fmt
        elif record.levelno == logging.WARNING:
            self._style._fmt = self.warn_fmt

        result = logging.Formatter.format(self, record)

        self._style._fmt = format_orig

        return result

class SplitStreamHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        if record.levelno == logging.INFO or \
           record.levelno == logging.DEBUG:
            stream = sys.stdout
        else:
            stream = sys.stderr

        stream.write(f"{msg}\n")
        stream.flush()


if __name__ == '__main__':
    parser = parser.parser()
    args = parser.parse_args()

    if args.config:
        args = Config.load(args)

    if not os.path.exists(DIR):
        os.mkdir(DIR)

    fmt = MyFormatter(args.verbose_position)
    hdlr = SplitStreamHandler()
    hdlr.setFormatter(fmt)
    logging.root.addHandler(hdlr)
    logging.root.setLevel(logging.ERROR)
    if args.verbose:
        if args.verbose == "debug":
            #logging.basicConfig(level=logging.DEBUG)
            logging.root.setLevel(logging.DEBUG)
        elif args.verbose == "info":
            #logging.basicConfig(level=logging.INFO)
            logging.root.setLevel(logging.INFO)
        elif args.verbose == "warning":
            #logging.basicConfig(level=logging.WARNING)
            logging.root.setLevel(logging.WARNING)
    Output.init()
    st_analysis = StaticAnalysis(args, DIR)
    DynamicAnalysis(st_analysis.manifest.package, args, st_analysis._StaticAnalysis__basepath)
