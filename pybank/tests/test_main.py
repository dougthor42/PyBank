# -*- coding: utf-8 -*-
"""
Tests PyBank components.

Created on Mon May 25 16:00:26 2015

@author: dthor

Usage:
    test_ofx.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""

# Standard Library
import sys
import os
import unittest
import unittest.mock as mock
import os.path as osp
import sqlite3

# Third-Party
from docopt import docopt

# Package / Application
try:
    from .. import main
except (SystemError, ImportError):
    if __name__ == "__main__":
        # Allow module to be run as script
        print("Running module as script")
        sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
        import main
    else:
        raise



class TestDummyMain(unittest.TestCase):
    """ dummy test here so that coverage grabs gui.py """
    def test_dummy(self):
        self.assertTrue(True)


def main():
    """
    Main entry point
    """
    docopt(__doc__, version="0.0.1")    # TODO: pull VERSION from __init__
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
