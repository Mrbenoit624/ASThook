import subprocess
import sys

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
