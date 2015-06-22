# -*- coding: utf-8 -*-
"""
Tests GUI components.

Created on Tue May 12 13:32:22 2015

Usage:
    test_gui.py

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
    from .. import gui
except (SystemError, ImportError):
    if __name__ == "__main__":
        # Allow module to be run as script
        print("Running module as script")
        sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
        import gui
    else:
        raise


class TestDummy(unittest.TestCase):
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
