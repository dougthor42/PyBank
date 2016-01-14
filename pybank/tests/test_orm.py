# -*- coding: utf-8 -*-
"""
Tests ORM components.

Created on Mon Jan  4 14:56:42 2016

Usage:
    test_orm.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""
# Standard Library
import sys
import unittest
import os.path as osp

# Third-Party
from docopt import docopt

# Package / Application
try:
    from .. import orm
    from ..__init__ import __version__
except (SystemError, ImportError):
    if __name__ == "__main__":
        # Allow module to be run as script
        print("Running module as script")
        sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
        import orm
    else:
        raise


THIS_DIR = osp.dirname(osp.abspath(__file__))


class ORMTestCase(unittest.TestCase):
    """ Creates and destroys the ORM engine and session """
    @classmethod
    def setUpClass(cls):
        cls.engine = orm.engine
        cls.session = orm.session

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.engine.dispose()


class TestCopyToSA(ORMTestCase):
    """ """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()        # make sure to run the parent's setUpClass
        dump_file = osp.join(THIS_DIR, "data", "temp_dump_file.txt")
        with open(dump_file, 'rb') as openf:
            dump = openf.read()
        cls.dump = dump.decode('utf-8').split(";")

    def test_copy_to_sa(self):
        try:
            orm.copy_to_sa(self.engine, self.session, self.dump)
        except Exception as err:
            self.fail("copy_to_sa raised exception: {}".format(err))


@unittest.skip("Needs complete rewrite")
class TestIterDump(ORMTestCase):
    """ """
    def setUp(self):
        """ copy the test dump file to the database and also read it """
        dump_file = osp.join(THIS_DIR, "data", "temp_dump_file.txt")
        orm.copy_to_sa(self.engine, self.session, dump_file)

        with open(dump_file, 'rb') as openf:
            self.dump = openf.read()
        self.dump = self.dump.decode('utf-8').split(";")[:-1]
        self.dump = list(x + ";" for x in self.dump)

    def test_sqlite_iterdump(self):
        new_dump = list(orm.sqlite_iterdump(self.engine, self.session))
#        new_dump = "".join(line for line in new_dump)
#        result = new_dump.encode('utf-8')
        result = list(x for x in new_dump)
        self.assertEqual(result, self.dump)


@unittest.skip("Needs to be written")
class TestDumpToFile(ORMTestCase):
    """ """
    def setUp(self):
        pass

    def test_dump_to_file(self):
        pass


class TestInsertFunctions(ORMTestCase):
    """ """
    def test_insert_account_group(self):
        try:
            orm.insert_account_group("NewAccountGroup")
        except Exception as err:
            self.fail("insert_account_group raised exception: {}".format(err))

    def test_insert_account(self):
        try:
            orm.insert_account(name="MyAccount",
                               acct_num="123456",
                               user="test_runner",
                               institution_id=None,
                               acct_group=None)
        except Exception as err:
            self.fail("insert_account raised exception: {}".format(err))

    def test_insert_category(self):
        try:
            orm.insert_category("Category1", 1)
        except Exception as err:
            self.fail("insert_category raised exception: {}".format(err))

    def test_insert_display_name(self):
        try:
            orm.insert_display_name("DisplayName")
        except Exception as err:
            self.fail("insert_display_name raised exception: {}".format(err))

    def test_insert_institution(self):
        try:
            orm.insert_institution("Institution")
        except Exception as err:
            self.fail("insert_institution raised exception: {}".format(err))

    def test_insert_memo(self):
        try:
            orm.insert_memo("Memo")
        except Exception as err:
            self.fail("insert_memo raised exception: {}".format(err))

    def test_insert_payee(self):
        try:
            orm.insert_payee("PayeeName")
        except Exception as err:
            self.fail("insert_payee raised exception: {}".format(err))

    @unittest.skip("Needs update")
    def test_insert_transaction(self):
        try:
            orm.insert_transaction()
        except Exception as err:
            self.fail("insert_transaction raised exception: {}".format(err))

    def test_insert_transaction_label(self):
        try:
            orm.insert_transaction_label("Label")
        except Exception as err:
            self.fail("insert_transaction_label raised exception: {}".format(err))

    def test_insert_ledger(self):
        try:
            orm.insert_ledger()
        except Exception as err:
            self.fail("insert_ledger raise exception: {}".format(err))


def main():
    """
    Main entry point
    """
    docopt(__doc__, version=__version__)
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
