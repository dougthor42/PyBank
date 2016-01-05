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
from enum import Enum, unique

# Third-Party
from docopt import docopt
import wx.grid

# Package / Application
try:
    # Imports used by unit test runners
    from . import __version__
#    from . import pbsql
    logging.debug("Imports for utils.py complete (Method: UnitTest)")
except SystemError:
    try:
        # Imports used by Spyder
        from __init__ import __version__
#        import pbsql
        logging.debug("Imports for utils.py complete (Method: Spyder IDE)")
    except ImportError:
         # Imports used by cx_freeze
        from pybank import __version__
#        from pybank import pbsql
        logging.debug("Imports for utils.py complete (Method: Executable)")

# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------
DEFAULT_LOG_LEVEL = logging.INFO
TEXT = wx.grid.GRID_VALUE_TEXT
STRING = wx.grid.GRID_VALUE_STRING

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


@unique
class LedgerCols(Enum):
    """
    Ledger Column Definitions

    (index, name, view col name, type, width)
    """
    tid = (0, "tid", "transaction_id", STRING, 30)
    date = (1, "Date", "date", TEXT, 100)
    enter_date = (2, "Date Entered", "enter_date", TEXT, 100)
    check_num = (3, "CheckNum", "check_num", TEXT, 80)
    payee = (4, "Payee", "Payee", TEXT, 120)
    dl_payee = (5, "Downloaded Payee", "DownloadedPayee", TEXT, 120)
    memo = (6, "Memo", "Memo", TEXT, 150)
    category = (7, "Category", "Category", TEXT, 180)
    label = (8,"Label", "TransactionLabel", TEXT, 160)
    amount = (9, "Amount", "Amount", TEXT, 80)
    balance = (10, "Balance", None, TEXT, 80)

    def __init__(self, index, col_name, view_name, col_type, width):
        self.index = index
        self.col_name = col_name
        self.view_name = view_name
        self.col_type = col_type
        self.width = width


# ---------------------------------------------------------------------------
### Functions
# ---------------------------------------------------------------------------
def logged(func):
    """
    Decorator that logs entry and exit points of a function.


    """
    # Customize these messages
    entry_msg = '+Entering  `{}`'
    exit_msg = '-Exiting   `{}`. Exec took {:.6}ms'
    logger = logging.getLogger()

    overrides = {'name_override': func.__qualname__,
                 'module_override': func.__module__,
                 }

    @functools.wraps(func)
    def wrapper(*args, **kwds):
        logger.debug(entry_msg.format(func.__name__), extra=overrides)
        start = time.perf_counter()
        f_result = func(*args, **kwds)
        end = time.perf_counter()
        elapsed = (end - start) * 1000
        logger.debug(exit_msg.format(func.__name__, elapsed), extra=overrides)
        return f_result
    return wrapper


def _init_logging(target, level=DEFAULT_LOG_LEVEL):
    """
    Initialize logging to the on-screen gui log text control
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

    for item in LedgerCols:
        print(item)
        print(item.index)