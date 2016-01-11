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
import decimal
from enum import Enum, unique

# Third-Party
from docopt import docopt
import wx.grid

# Package / Application
try:
    # Imports used by unit test runners
    from . import __version__
    from . import constants
    logging.debug("Imports for utils.py complete (Method: UnitTest)")
except SystemError:
    try:
        # Imports used by Spyder
        from __init__ import __version__
        import constants
        logging.debug("Imports for utils.py complete (Method: Spyder IDE)")
    except ImportError:
         # Imports used by cx_freeze
        from pybank import __version__
        from pybank import constants
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
    category = (7, "Category", "Category", TEXT, 240)
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


#def log_entire_class(cls):
#    """
#    Decorator that logs the entry and exit points for each method in
#    a class.
#
#    From David Beazley's "Python 3 Metaprogramming" Talk
#        http://www.dabeaz.com/py3meta/
#        PyCon'13 (2014-03-14, Santa Clara, CA)
#
#    TODO: Actually get working...
#    """
#    for name, val in vars(cls).items():
#        if callable(val):
#            setattr(cls, name, logged(val))
#        return cls


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


def moneyfmt(value, places=2,
             curr=constants.CURRENCY_SYM,
             sep=constants.THOUSANDS_SEP,
             dp=constants.DECIMAL_MARK,
             pos='', neg='-', trailneg='',
             trailcur=constants.TRAILING_CURRENCY_SYM):
    """Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank
    trailcur:optional trailing currency symbol

    >>> from decimal import Decimal
    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, curr='', places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), curr='', sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), curr='', neg='<', trailneg='>')
    '<0.02>'

    # Shamelessly taken from the Python Docs on 2016-01-08
    # https://docs.python.org/3/library/decimal.html#recipes
    # and modified to allow for the currency symbol as a suffix.
    """
    q = decimal.Decimal(10) ** -places      # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = list(map(str, digits))
    build, next = result.append, digits.pop
    if trailcur:
        build(trailcur)
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    if places:
        build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))


def build_category_strings(cat_list,
                           delimiter=".",
                           parent_item=None,
                           sent_str=None,
                           retval=None,
                           ):
    """
    Recursively concatenates categories together and returns a list of them.

    Parameters:
    -----------
    cat_list : list of (id, name, parent) tuples
        The data to create strings from. This must be a list (or list-like)
        of (id, name, parent_id) tuples (or list-like).

    delimiter: string
        The string to put between each item.

    parent_item :
        Only used during recursion.

    sent_str :
        Only used during recursion

    retlist :
        Only used during recursion.

    Returns:
    --------
    retlist : list of strings
        A list of dot-notation strings.

    Examples:
    ---------

    >>> data = [(1, "A", 0), (2, "B", 1), (3, "C", 1), (4, "D", 2),
    ...         (5, "E", 2), (6, "F", 3), (7, "G", 2), (8, "H", 6),
    ...         ]
    >>> build_category_strings(data)
    ['A', 'A.B', 'A.B.D', 'A.B.E', 'A.B.G', 'A.C', 'A.C.F', 'A.C.F.H']

    """
    if retval is None:
        retval = []

    if parent_item is None:
        parent_item = cat_list[0]
        retval.append(parent_item[1])

    parent_id = parent_item[0]
    parent_name = parent_item[1]

    if sent_str is None:
        sent_str = parent_name

    # Find the children
    children = [_x for _x in cat_list if _x[2] == parent_id]

    if len(children) == 0:
        # base case (no children), so we return the full path
        return ["{}{}{}".format(sent_str, delimiter, parent_name)]
    else:
        # children exist so we need to iterate through them.
        for child in children:
            # create an incomplete path string and add it to our return value
            str_to_send = "{}{}{}".format(sent_str, delimiter, child[1])
            retval.append(str_to_send)
            # recurse using the current child as the new parent
            build_category_strings(cat_list,
                                      delimiter,
                                      child,
                                      str_to_send,
                                      retval)
        return retval


def build_category_string(item, data, delimiter=":", max_nest=10):
    """
    Builds a single category string from an Adjacency List structure.

    This function assumes that the adjacency list primary key starts at 1.

    If item == 0, then an empty string '' is returned.

    If ``item`` is not found (for example, ``len(data) == 5`` and
    ``item == 7``), then ``'!! None !!'`` is returned.

    Parameters:
    -----------
    item : int
        The primary key of the item to build a string for

    data : list
        The adjacency list in the format of [(pk, name, parent_pk), ...]

    delimiter : string, default colon ':'
        The string to separate the nesting levels with

    max_nest : int, default 10
        The maximum number of nesting levels to traverse before returning.

    Returns:
    --------
    string : str
        The lineage string in the format of: oldest -> youngest separated by
        `delimiter`.

    Examples:
    ---------

    >>> data = [(1, "Expense", 1), (2, "Income", 2), (3, "Auto", 2),
    ...         (4, "Fees", 3), (5, "Gas", 3), (6, "Insurance", 3),
    ...         (7, "Bank Fees", 1), (8, "Commissions", 2),
    ...         (9, "Salaray", 2), (10, "Bonus", 9), (11, "Holiday", 9),
    ...         ]
    >>> build_category_strings(10, data)
    Income:Salaray:Bonus

    """
    parent = None
    values = []

    # If None, empty string, or 0, return empty string.
    if not item:
        return ''

    while True:
        try:
            # I don't just use a `data[item - 1]` because... ?
            item, value, parent = list((row
                                        for row in data
                                        if row[0] == item))[0]
        except IndexError:
            logging.warning("item not found.")
            return "!! None !!"

        # update the lineage list
        values.append(value)

        # return the string if we're at the top level
        if parent == item:
            break

        # Set the parent to be the next item we search for.
        item = parent

        # Check for the max nesting level
        max_nest -= 1
        if max_nest <= 0:
            logging.warning("Maximum number of nesting levels reached")
            break

    return delimiter.join(reversed(values))


def main():
    """
    Main entry point
    """
    docopt(__doc__, version=__version__)
    print("Running utils.py")

    logging.debug("debugging")
#    logging.info("Info!")
#    logging.warning("warning: you can't do anything about this")
#    logging.error("error")
#    logging.critical("critical")
#    logging.exception("exception")

    print("End")
    a = find_data_file('PyBank.py')
    print(a)




if __name__ == "__main__":
#    main()
#
#    for item in LedgerCols:
#        print(item)
#        print(item.index)
    d = decimal.Decimal("1123213.232032")
    print(moneyfmt(d, curr='>'))

    data = [(1, "Expense", 1),
            (2, "Income", 2),
            (3, "Auto", 2),
            (4, "Fees", 3),
            (5, "Gas", 3),
            (6, "Insurance", 3),
            (7, "Bank Fees", 1),
            (8, "Commissions", 2),
            (9, "Salaray", 2),
            (10, "Bonus", 9),
            (11, "Holiday", 9),
            ]


    print(build_category_string(10, data))
    print(build_category_string(7, data, "."))
    print(build_category_string(5, data, ":"))
