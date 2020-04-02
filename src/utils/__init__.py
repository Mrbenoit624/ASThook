from contextlib import contextmanager
import signal


def bprint(text):
    """
    Create a beautiful print
    """
    size = int(len(text)/2)
    print()
    print("#" * 80)
    print("%s%s" % (" " * (40 - size), text))
    print("#" * 80, end='\n\n')

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

