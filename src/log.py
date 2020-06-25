import subprocess
import sys
import logging

from pathlib import Path
from sty import fg, bg, ef, rs, Style, RgbFg
#from utils import bprint, warning, info, error, good
import utils


class MyFormatter(logging.Formatter):

    def __init__(self, position):
        super().__init__(fmt="%(levelno)d: %(msg)s", datefmt=None, style='%')  
        if position:
            self.position = utils.warning("[ %(pathname)s : %(lineno)s ]")
        else:
            self.position = ""

        base = fg.cyan + " [%(asctime)s]" + fg.rs +" %(msg)s"
        self.err_fmt  = utils.error("[!]") + self.position + base
        self.warn_fmt = utils.warning("[-]") + base
        self.dbg_fmt  = utils.good("[?]") + self.position + " %(msg)s"
        self.info_fmt = utils.info("[*]") + base

    def format(self, record):

        format_orig = self._style._fmt

        npath = Path(__file__).parent.absolute()
        
        #if str(record.pathname).startswith(str(npath)):
        record.pathname = Path(record.pathname).relative_to(npath)
        #else:
        #    self._style._fmt = format_orig
        #    return "" #logging.Formatter.format(self, record)
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



class Log:
    """
    Class manage logs
    """

    @classmethod
    def __init__(cls, verbose):
        """
        setup if verbose all stdout and stderr will be printed
        """
        if verbose:
            cls.STD_OUTPOUT = sys.stdout
            cls.STD_ERR = sys.stderr
        else:
            cls.STD_OUTPOUT = subprocess.DEVNULL
            cls.STD_ERR = subprocess.DEVNULL

def setup_logger(args):
    fmt = MyFormatter(args.verbose_position)
    hdlr = SplitStreamHandler()
    hdlr.setFormatter(fmt)
    hdlr.setLevel(logging.ERROR)
    logger = logging.getLogger("phone_analysis")
    logger.setLevel(logging.ERROR)
    logger.propagate = 0
    if args.verbose:
        if args.verbose == "debug":
            #logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            hdlr.setLevel(logging.DEBUG)
        elif args.verbose == "info":
            #logging.basicConfig(level=logging.INFO)
            logger.setLevel(logging.INFO)
            hdlr.setLevel(logging.INFO)
        elif args.verbose == "warning":
            #logging.basicConfig(level=logging.WARNING)
            logger.setLevel(logging.WARNING)
            hdlr.setLevel(logging.WARNING)
    logger.addHandler(hdlr)
    #Logger.init(logger)

def debug(msg):
    #print(logging.getLogger("phone_analysis").handlers)
    logging.getLogger("phone_analysis").debug(msg)

def info(msg):
    logging.getLogger("phone_analysis").info(msg)

def warning(msg):
    logging.getLogger("phone_analysis").warning(msg)

def error(msg):
    logging.getLogger("phone_analysis").error(msg)
