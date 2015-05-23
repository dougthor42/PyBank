# -*- coding: utf-8 -*-
"""
Tests OFX components.

Created on Tue May 12 13:31:46 2015

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
import ofx


class TestSaltAndHash(unittest.TestCase):
    """
    Tests the ofx.salt_and_hash function
    """

    def test_no_collisions(self):
        """
        Make sure that there are no collisions by calling the function
        with the same arguements many times
        """
        secret = "SuperSecretPassword"
        sah = ofx.salt_and_hash
        hashbrowns = [sah(secret)[1]]
        for _ in range(512):
            value = sah(secret)[1]
            hashbrowns.append(value)
            self.assertNotIn(value, hashbrowns[:-1])


class TestValidatePassword(unittest.TestCase):
    """
    Tests that salted and hashed passwords are correctly validated.
    """
    def setUp(self):
        self.secret = "This is my Secret"
        self.wrong_secret = "This is my secret"
        self.salt, self.hashed = ofx.salt_and_hash(self.secret)

    def test_good_validation(self):
        result = ofx.validate_password(self.secret, self.salt, self.hashed)
        self.assertTrue(result)

    def test_bad_validation(self):
        result = ofx.validate_password(self.wrong_secret,
                                       self.salt,
                                       self.hashed)
        self.assertFalse(result)


def main():
    """
    Main entry point
    """
    docopt(__doc__, version="0.0.1")    # TODO: pull VERSION from __init__
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
