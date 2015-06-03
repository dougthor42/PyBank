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
#from __init__ import VERSION
from pybank import pbsql


class MyProductionClass():
    pass


class TestGenerateCategoryStrings(unittest.TestCase):
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

        data = [(1, "A", 0),
                (2, "B", 1),
                (3, "C", 1),
                (4, "D", 2),
                (5, "E", 2),
                (6, "F", 3),
                (7, "G", 2),
                (8, "H", 6),
                (9, "I", 4),
                ]

        actual = ["A",
                  "A.B",
                  "A.B.D",
                  "A.B.D.I",
                  "A.B.E",
                  "A.B.G",
                  "A.C",
                  "A.C.F",
                  "A.C.F.H",
                  ]

        result = pbsql.generate_category_strings(data)
        self.assertEqual(result, actual)


class TestMock(unittest.TestCase):
    """
    """
    def test_mock(self):
        thing = MyProductionClass()
        thing.method = mock.MagicMock(return_value=3)
        a = thing.method(3, 4, 5, key='value')
        thing.method.assert_called_with(3, 4, 5, key='value')


def main():
    """
    Main entry point
    """
    docopt(__doc__, version="0.0.1")    # TODO: pull VERSION from __init__
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
