# -*- coding: utf-8 -*-
"""
Various utilities used by PyBank.

Created on Tue May 12 13:30:56 2015

Usage:
    utils.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.
"""
# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
#import sys
#import os.path as osp
import logging
import functools
import time
import sys
import os.path

# Third-Party
from docopt import docopt

# Package / Application
try:
    # Imports used by unit test runners
#    from . import pbsql
    from . import __version__
    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
#        import pbsql
        from __init__ import __version__
        logging.debug("Imports for Spyder IDE")
    except ImportError:
         # Imports used by cx_freeze
#        from pybank import pbsql
        from pybank import __version__
        logging.debug("imports for Executable")

# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------
DEFAULT_LOG_LEVEL = logging.INFO

# ---------------------------------------------------------------------------
### Classes
# ---------------------------------------------------------------------------
class LocalLogHandler(logging.StreamHandler):
    """
    A logging handler that directs logs to a ``target`` wx.TextCtrl.
    """
    def __init__(self, target):
        logging.StreamHandler.__init__(self)
        self.target = target

    def emit(self, record):
        msg = self.format(record)
        self.target.WriteText(msg + "\n")
        self.target.ShowPosition(self.target.GetLastPosition())
        self.flush()

# ---------------------------------------------------------------------------
### Functions
# ---------------------------------------------------------------------------
def logged(func):
    """
    Decorator that logs entry and exit points of a function.

    TODO: make is to the logging handler correct gets the funcName
    """
    # Customize these messages
    entry_msg = '+Entering  {}'
    exit_msg = '-Exiting   {}. Exec took {:.6}ms'
    logger = logging.getLogger()

    @functools.wraps(func)
    def wrapper(*args, **kwds):
        logger.debug(entry_msg.format(func.__name__))
        start = time.perf_counter()
        f_result = func(*args, **kwds)
        end = time.perf_counter()
        elapsed = (end - start) * 1000
        logger.debug(exit_msg.format(func.__name__, elapsed))
        return f_result
    return wrapper


def _init_logging(target, level=DEFAULT_LOG_LEVEL):
    """
    Initialize logging to the on-screen log
    """

    logfmt = ("%(asctime)s.%(msecs)03d"
              " [%(levelname)-8.8s]"    # Note implicit string concatenation.
              "  %(message)s"
              )
    datefmt = "%Y-%m-%d %H:%M:%S"
#    datefmt = "%H:%M:%S"

    logger = logging.getLogger()
    handler = LocalLogHandler(target)
    handler.setLevel(level)
    formatter = logging.Formatter(logfmt, datefmt)
    handler.setFormatter(formatter)
    handler.set_name("GUI Handler")
    logger.addHandler(handler)

    logging.info("GUI Logging Initialized, level = {}".format(level))


def find_data_file(filename):
    """ Something """
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)

    return os.path.join(datadir, filename)

def main():
    """
    Main entry point
    """
    docopt(__doc__, version=__version__)
    print("Running utils.py")

    logging.debug("debugging")
#    logging.info("Info!")
#    logging.warn("warn: you should do this instead")
#    logging.warning("warning: you can't do anything about this")
#    logging.error("error")
#    logging.critical("critical")
#    logging.exception("exception")

    print("End")
    a = find_data_file('PyBank.py')
    print(a)


if __name__ == "__main__":
    main()
