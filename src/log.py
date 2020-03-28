import subprocess
import sys

class Log:

    @classmethod
    def __init__(cls, verbose):
        if verbose:
            cls.STD_OUTPOUT = sys.stdout
            cls.STD_ERR = sys.stderr
        else:
            cls.STD_OUTPOUT = subprocess.DEVNULL
            cls.STD_ERR = subprocess.DEVNULL
