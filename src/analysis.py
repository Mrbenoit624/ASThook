import os
import logging

from sty import fg, bg, ef, rs, Style, RgbFg
from utils import bprint, warning, info, error, good

from static import StaticAnalysis
from dynamic import DynamicAnalysis
from log import Log
from config import Config
import parser
from utils import Output

DIR="temp"

fg.blue = Style(RgbFg(54,154,205))
class MyFormatter(logging.Formatter):

    base = fg.cyan + " [%(asctime)s]" + fg.rs +" %(msg)s"
    err_fmt  = error("[!]") + base
    warn_fmt = warning("[-]") + base
    dbg_fmt  = good("%(msg)s")
    info_fmt = info("[*]") + base

    def __init__(self):
        super().__init__(fmt="%(levelno)d: %(msg)s", datefmt=None, style='%')  

    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._style._fmt = MyFormatter.dbg_fmt

        elif record.levelno == logging.INFO:
            self._style._fmt = MyFormatter.info_fmt

        elif record.levelno == logging.ERROR:
            self._style._fmt = MyFormatter.err_fmt
        
        elif record.levelno == logging.WARNING:
            self._style._fmt = MyFormatter.warn_fmt

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


if __name__ == '__main__':
    parser = parser.parser()
    args = parser.parse_args()

    if args.config:
        args = Config.load(args)

    if not os.path.exists(DIR):
        os.mkdir(DIR)

    Log(False)
    fmt = MyFormatter()
    hdlr = logging.StreamHandler()
    hdlr.setFormatter(fmt)
    logging.root.addHandler(hdlr)
    logging.root.setLevel(logging.ERROR)
    if args.verbose:
        Log(True)
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
