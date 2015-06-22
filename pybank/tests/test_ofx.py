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
try:
    from .. import ofx
except (SystemError, ImportError):
    if __name__ == "__main__":
        # Allow module to be run as script
        print("Running module as script")
        sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
        import ofx
    else:
        raise


class TestSaltAndHash(unittest.TestCase):
    """
    Tests the ofx.salt_and_hash function
    """

    def test_no_collisions(self):
        """
        Check for collisions by calling the salt_and_hash many times
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
        """ Check that a correct password validates True """
        result = ofx.validate_password(self.secret, self.salt, self.hashed)
        self.assertTrue(result)

    def test_bad_validation(self):
        """ Check that an incorrect password validates False """
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
