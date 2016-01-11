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
from decimal import Decimal as D

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
                result = utils.build_cat_string(data[0], self.data)
                self.assertEqual(result, expected)

    def test_invalid_item(self):
        for item in self.invlaid_items:
            with self.subTest(item=item):
                result = utils.build_cat_string(item, self.data)
                self.assertEqual(result, "")

    def test_item_not_found(self):
        result = utils.build_cat_string(15, self.data)
        self.assertEqual(result, "!! None !!")


class TestMoneyFmt(unittest.TestCase):
    """
    Test the moneyfmt function.

    Shoudln't need much since it was taken from the python docs...
    """
    def test_known_values(self):
        known_values = (({"value": D("1.23"),
                          "places": 2,
                          "curr": "$",
                          "sep": ",",
                          "dp": ".",
                          "pos": "",
                          "neg": "-",
                          "trailneg": "",
                          "trailcur": ""}, "$1.23"),
                         ({"value": D("1563.126"),
                          "places": 2,
                          "curr": "$",
                          "sep": ",",
                          "dp": ".",
                          "pos": "",
                          "neg": "-",
                          "trailneg": "",
                          "trailcur": ""}, "$1,563.13"),
                        )
        for params, expected in known_values:
            with self.subTest(value=params["value"]):
                result = utils.moneyfmt(**params)
                self.assertEqual(result, expected)

    def test_places(self):
        value = D("1.234567890123456")
        known_places = ((0, "$1"),
                        (1, "$1.2"),
                        (2, "$1.23"),
                        (3, "$1.235"),
                        (4, "$1.2346"),
                        )
        for places, expected in known_places:
            with self.subTest(num_decimal=places):
                result = utils.moneyfmt(value, places=places)
                self.assertEqual(result, expected)

    def test_curr(self):
        value = D("1.23")
        known_currs = (("", "1.23"),
                       ("$", "$1.23"),
                       ("#", "#1.23"),
                       ("¥", "¥1.23"),
                       (">", ">1.23"),
                       )
        for curr, expected in known_currs:
            with self.subTest(currency_sym=curr):
                result = utils.moneyfmt(value, curr=curr)
                self.assertEqual(result, expected)

    def test_sep(self):
        value = D("1234567.89")
        known_seps = (("", "$1234567.89"),
                      (",", "$1,234,567.89"),
                      (".", "$1.234.567.89"),
                      ("|", "$1|234|567.89"),
                      ("*", "$1*234*567.89"),
                      )
        for sep, expected in known_seps:
            with self.subTest(seperator_sym=sep):
                result = utils.moneyfmt(value, sep=sep)
                self.assertEqual(result, expected)


def main():
    """
    Main entry point
    """
    docopt(__doc__, version="0.0.1")    # TODO: pull VERSION from __init__
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()

