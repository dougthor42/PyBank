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

### #------------------------------------------------------------------------
### Imports
### #------------------------------------------------------------------------
# Standard Library
import sys
import os.path as osp

# Third-Party
from docopt import docopt

# Package / Application
if __name__ == "__main__":
    sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
#from __init__ import VERSION
from parseofx import ParseOFX


### #------------------------------------------------------------------------
### Module Constants
### #------------------------------------------------------------------------


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
    """
    pass



def main():
    """
    Main entry point
    """
    docopt(__doc__, version="0.0.1")    # TODO: pull VERSION from __init__


if __name__ == "__main__":
    main()
