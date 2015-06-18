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
import os
import unittest
import unittest.mock as mock
import os.path as osp
import sqlite3

# Third-Party
from docopt import docopt

# Package / Application
#if __name__ == "__main__":
#    sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
#from __init__ import VERSION
from pybank import pbsql


class TestGenerateCategoryStrings(unittest.TestCase):
    """ Tests relating to generate_category_strings """
    @unittest.skip("come back to this later")
    def test_testfunc(self):
        """ generate_category_strings"""
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


class TestDatabase(unittest.TestCase):
    """ Test database actions """
    @classmethod
    def setUpClass(cls):
        """ Create a database file to work on for these tests. """
        cls._db = "unittest_db.db"
        pbsql.create_db(cls._db)

    @classmethod
    def tearDownClass(cls):
        """ Destroy temporary file """
        os.remove(cls._db)

#    @unittest.skip("Need to refactor create_db")
#    def test_create_db(self):
#        """ Verify database created OK """
#        try:
#            pbsql.create_db(self._db)
#        except Exception:
#            self.fail("Unexpected exception in db_execute")

    def test_create_trans_tbl(self):
        """ Check transaction table is created """
        try:
            pbsql.create_trans_tbl(self._db, 1)
            # TODO: should pass only if acct is int >= 0
        except Exception:
            self.fail("Unexpected exception in create_trans_tbl")

    # TODO: fails if test_create_trans_tbl is not executed before this.
    #       however, it's implicitely checked in test_create_db
    @unittest.skip("Race condition")
    def test_create_ledger_view(self):
        """ Check ledger view is created """
        try:
            pbsql.create_ledger_view(self._db, 1)
        except Exception:
            self.fail("Unexpected exceptoin in create_ledger_view")

    def test_db_execute(self):
        """ Check execute command """
        cmd = """
            CREATE TABLE stocks
            (date text, trans text, symbol text, qty real, price real)
            """
        try:
            pbsql.db_execute(self._db, cmd)
        except Exception:
            self.fail("Unexpected exception in db_execute")

    def test_db_query(self):
        """ Check query command """
        cmd = "SELECT * FROM payee"
        result = pbsql.db_query(self._db, cmd)
        self.assertEqual(result, [])

    def test_db_insert(self):
        """ Check insert Command """
        cmd = "INSERT INTO display_name (display_name) VALUES (?)"
        value = 'hello'
        result = pbsql.db_insert(self._db, cmd, value)
        self.assertEqual(result, 1)


@unittest.skip("Placeholder Test")
class TestMock(unittest.TestCase):
    """
    """
    def test_mock(self):
        """ example of mocking """
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
