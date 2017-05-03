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
import unittest
import os.path as osp

# Third-Party

# Package / Application
from .. import orm


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


@unittest.skip("Needs to be written")
class TestDumpToFile(ORMTestCase):
    """ """
    def setUp(self):
        pass

    def test_dump_to_file(self):
        pass



