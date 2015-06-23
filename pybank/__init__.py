# -*- coding: utf-8 -*-
"""
PyBank
============

This program is supposed to be a tracker for finances and money.

Basic Goals:
------------

1.  Able to download transactions via OFX
2.  Save transaction register to a local db

    + Eventually encrypt
    + SQLite

3.  Able to plot funds vs time.
4.  List transactions in a register-like GUI, similar to Quicken


List of Modules:
----------------

main:
    Main module, do not include much in this. It should just call the gui
    module and start the program running. I think.
gui:
    Contains the UI elements. This should be completely separate from
    anything else so that I can updated it without having to modify other
    modules.

    Do I want to separate out each GUI component into different modules? For
    example: mainpanel.py, mainframe.py, mainapp.py, ledger.py, accts_list.py,
    etc.?

    For now, it will all stay in one file.
sqlite:
    Contains the SQLite actions - reading the .db file, editing and inserting
    new elements, saving the file, etc.
ofx:
    Handles the downloading and parsing of the OXF file via the ofxparse and
    ofxclient external modules
utils:
    Contains various utilities required. I haven't decided if I will put the
    matching/renaming functions in here or somewhere else.

Overall Program Flow:
---------------------

+ User opens program, chooses db file.
    + prompt for vault password
        + decrypt database file?    # XXX: have to ensure encryption later
+ Check for existing database
    + create if DNE, validate if exist
+ User creates new account
    + Prompt for institution information
        + Save to DB
    + Prompt for username and password
        + Save username to DB, password to keyring
    + List accounts available
    + User chooses one
    + Download transactions
    + Store transactions in new acct table
        + reserve 1st line for opening balance
    + Ask user for opening balance

GUI:
----
The GUI will be an important part of the program. Here is where I'll
brainstorm ideas on how it will look and act.

+ Use wx.RibbonBar for menus (but start off with standard MenuBar or have
  the MenuBar still exist above the RibbonBar). Possibly wx.ToolBar.
+ Use wx.Toolbook or wx.Notebook for various tabs/pages (ledger, summary,
  graphs, etc.).
+ Initially two panes: AccountList and Legder.

  + Perhaps later add a 3rd: maybe I want a graph on the bottom?
  + Account List should show name and current balance. Should also show totals
    for that group and overall.
  + Ledger will be a standard excel-like table, but pretty.
  + Bottom of ledger should show online balance, online available balance,
    and current ledger balance. Anything else?

+ Use wx.PopupMenu for right-click items.
+ Probably use wx.ListCtrl_virtual for the transaction ledger.
  + OR DataViewListCtrl
  + UltimateListCtrl
+ wx.TreeControl or wx.TreeListControl for account list?
+ wx.ComboBox for Category, Label

  + Possibly wx.FoldPanelBar? Not right now, since there's no drag-and-drop
    or reordering of items.

    + But that might be OK, since I can have the user set the account
      hierarchy somewhere else.
    + Screw it, it looks like. Let's go with it.

+ Don't use matplotlib for graphs - too heavy I think. But what's the
  alternative?

Notes:
------
I may have to re-write an OFX parser...

Transaction matching and download start date = previous download date.

# TODO: Category contactenation:
        Parent.Child.Grandchild
# TODO: Do I want to name transaction tables as transaction_0 or
        transaction_00? Or even transaction_000?
# TODO: Does Google Wallet have OFX?
"""
import logging
from logging.handlers import TimedRotatingFileHandler as TRFHandler
import datetime
import os.path


__version__ = "0.0.2.1"
__project_url__ = "https://github.com/dougthor42/PyBank"
__project_name__ = "PyBank"


__all__ = [__version__,
           __project_name__,
           __project_url__,
           ]

# Set up logging. DEBUG to console, INFO to file.
# see https://aykutakin.wordpress.com/2013/08/06/logging-to-console-and-file-in-python/
# Logging format includes milliseconds.
# See http://stackoverflow.com/a/7517430/1354930
logfmt = ("%(asctime)s.%(msecs)03d"     # Note implicit string concatenation.
          " [%(levelname)-8.8s]"
          " [%(module)-8.8s]"
          " [%(funcName)-10.10s]"
          "  %(message)s"
          )
datefmt = "%Y-%m-%d %H:%M:%S"

# Create the logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create console handler and set level
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(logfmt, datefmt)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Create file handler and set level
# Use a Rotating file handler so that each week has a different file.
# see https://docs.python.org/3.4/library/logging.handlers.html#logging.handlers.TimedRotatingFileHandler
# and http://www.blog.pythonlibrary.org/2014/02/11/python-how-to-create-rotating-logs/

# Build the logfile path.
dirname = os.path.dirname(os.path.abspath(__file__))
rootpath = os.path.split(dirname)[0]
logpath = os.path.join(rootpath, "log")
logfile = os.path.join(logpath, "PyBank.log")

rollover_time = datetime.time.min       # midnight
try:
    handler = TRFHandler(logfile,
                         when="W6",         # Sunday night
#                         interval=7,
#                         backupCount=5,
                         atTime=rollover_time,
#                         delay=True,
                         )
except FileNotFoundError:
    # we probably need to go up one more level to find the log folder
    rootpath = os.path.split(rootpath)[0]
    logpath = os.path.join(rootpath, "log")
    logfile = os.path.join(logpath, "PyBank.log")
    handler = TRFHandler(logfile,
                         when="W6",         # Sunday night
#                         interval=7,
#                         backupCount=5,
                         atTime=rollover_time,
#                         delay=True,
                         )


handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(logfmt, datefmt)
handler.setFormatter(formatter)
logger.addHandler(handler)
