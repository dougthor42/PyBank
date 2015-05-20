# -*- coding: utf-8 -*-
"""
Tests SQLite components

Created on Tue May 12 13:31:57 2015

Usage:
    test_ofx.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""

# Standard Library
import sys
import unittest
import unittest.mock as mock
import os.path as osp

# Third-Party
from docopt import docopt

# Package / Application
if __name__ == "__main__":
    sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
from __init__ import VERSION
import sqlite


class MyProductionClass():
    pass


class TestTestFunc(unittest.TestCase):
    """
    """
    def setUp(self):
        """ Runs begfore every test """
        pass

    def tearDown(self):
        """
        Runs after the tests if and only if the setUp succeeded. It does not
        depend on if the test succeeded or not.
        """
        pass

    def test_testfunc(self):
        self.assertEqual(sqlite.my_func(), 5)


class TestMock(unittest.TestCase):
    """
    """
    def test_mock(self):
        thing = MyProductionClass()
        thing.method = mock.MagicMock(return_value=3)
        a = thing.method(3, 4, 5, key='value')
        print(a)
        thing.method.assert_called_with(3, 4, 5, key='value')


def main():
    """
    Main entry point
    """
    docopt(__doc__, version=VERSION)
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
