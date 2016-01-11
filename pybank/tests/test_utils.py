# -*- coding: utf-8 -*-
"""
Tests utilities.

Created on Tue May 12 13:32:09 2015

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
    from .. import utils
except (SystemError, ImportError):
    if __name__ == "__main__":
        # Allow module to be run as script
        print("Running module as script")
        sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
        import utils
    else:
        raise



class TestBuildCategoryString(unittest.TestCase):
    """
    """
    data = [(1, "Expense", 1),
            (2, "Income", 2),
            (3, "Auto", 1),
            (4, "Fees", 3),
            (5, "Gas", 3),
            (6, "Insurance", 3),
            (7, "Bank Fees", 1),
            (8, "Commissions", 2),
            (9, "Salary", 2),
            (10, "Bonus", 9),
            (11, "Holiday", 9),
            ]

    known_values = ('Expense', 'Income',
                    'Expense:Auto', 'Expense:Auto:Fees', 'Expense:Auto:Gas',
                    'Expense:Auto:Insurance', 'Expense:Bank Fees',
                    'Income:Commissions', 'Income:Salary',
                    'Income:Salary:Bonus', 'Income:Salary:Holiday',
                    )

    invlaid_items = [0, None, '']

    def test_known_values(self):
        for data, expected in zip(self.data, self.known_values):
            with self.subTest(params=data):
                result = utils.build_category_string(data[0], self.data)
                self.assertEqual(result, expected)

    def test_invalid_item(self):
        for item in self.invlaid_items:
            with self.subTest(item=item):
                result = utils.build_category_string(item, self.data)
                self.assertEqual(result, "")

    def test_item_not_found(self):
        result = utils.build_category_string(15, self.data)
        self.assertEqual(result, "!! None !!")


def main():
    """
    Main entry point
    """
    docopt(__doc__, version="0.0.1")    # TODO: pull VERSION from __init__
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
