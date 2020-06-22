import os
import sys
from log import setup_logger
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

if __name__ == '__main__':
    parser = parser.parser()
    args = parser.parse_args()

    if args.config:
        args = Config.load(args)


    if not os.path.exists(DIR):
        os.mkdir(DIR)

    #fmt = MyFormatter(args.verbose_position)
    #hdlr = SplitStreamHandler()
    #hdlr.setFormatter(fmt)
    #logging.root.setLevel(logging.ERROR)
    #if args.verbose:
    #    if args.verbose == "debug":
    #        #logging.basicConfig(level=logging.DEBUG)
    #        logging.root.setLevel(logging.DEBUG)
    #    elif args.verbose == "info":
    #        #logging.basicConfig(level=logging.INFO)
    #        logging.root.setLevel(logging.INFO)
    #    elif args.verbose == "warning":
    #        #logging.basicConfig(level=logging.WARNING)
    #        logging.root.setLevel(logging.WARNING)
    #logging.root.addHandler(hdlr)
    setup_logger(args)
    Output.init()

    if args.restore_output:
        Output.load(args.restore_output)

    st_analysis = StaticAnalysis(args, DIR)
    DynamicAnalysis(st_analysis.manifest.package, args, st_analysis._StaticAnalysis__basepath)
