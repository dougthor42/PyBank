# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 13:19:21 2014

@name:          dtmoney.py
@vers:          0.1
@author:        dthor
@created:       Mon Jun 16 13:19:21 2014
@modified:      Mon Jun 16 13:19:21 2014
@descr:         DTMoney - a finance tracking system.
                This is the main module of the program. It contains the user
                interface options (though I don't plan on having many).

Usage:
    dtmoney.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""

from __future__ import print_function
from docopt import docopt
import ofxparse
import ofxclient
import sqlite3 as sql
#import tkinter as tk
import wx
import pybank


def main():
    """ Main Code """
    docopt(__doc__, version='v0.1')


if __name__ == "__main__":
    main()
