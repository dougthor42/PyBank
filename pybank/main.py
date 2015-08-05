# -*- coding: utf-8 -*-
"""
PyBank core module and main entry point.

Created on Mon May 25 15:57:10 2015

@author: dthor

Usage:
    oxf.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""

# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
import sys
import logging
import os.path

# Third-Party
from docopt import docopt

# Package / Application
# Package / Application
try:
    # Imports used for unittests
    from . import pbsql
    from . import __version__
    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
        import pbsql
        from __init__ import __version__
        logging.debug("Imports for Spyder IDE")
    except ImportError:
         # Imports used by cx_freeze
        from pybank import pbsql
        from pybank import __version__
        logging.debug("imports for Executable")


# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------


def save_account():
    """
    Save account info to the database.
    """
    pass

def save_institution():
    """
    Save institution info to the database.
    """
    pass

def read_institution():
    """
    Read insitution info from the database.
    """
    pass

def read_account():
    """
    Read account info from the database.
    """
    pass

def save_transaction():
    """
    Saves a transaction

    This function is the primary workhorse of the ledger.

    It needs to:

    1. find the payee in the payee table
        + find the category in the category table
        + find the payee display name in the display_name table

    """
    pass


def read_transaction():
    """
    Reads a single transaction from a transaction table.

    Handles the joining of tables so that only display_names are shown.

    Parameters:
    -----------
    account : int
        Account_ID from the acct table.

    Returns:
    --------
    data : tuple
        A tuple of the data to be used in the GUI.

    """
    pass


def get_transactions_for_gui(account):
    """
    Reads the entire transaction table for a given account and returns the
    data in a format that the gui will like.

    Parameters:
    -----------
    account : int
        Account_ID from the acct table

    Returns:
    --------
    data : dict
        Dictionary-formatted dataset for the gui.

    """


def main():
    """
    Main entry point
    """
    docopt(__doc__, version=__version__)
    print("Running pybank.py")
    print("End")


if __name__ == "__main__":
    main()
