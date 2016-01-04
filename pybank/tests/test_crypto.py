# -*- coding: utf-8 -*-
"""
Tests crypto components.

Created on Mon Jan  4 11:17:45 2016

Usage:
    test_crypto.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""
# Standard Library
import sys
import unittest
import unittest.mock as mock
import os.path as osp
import logging

# Third-Party
from docopt import docopt
import keyring

# Package / Application
try:
    from .. import crypto
    from ..__init__ import __version__
except (SystemError, ImportError):
    if __name__ == "__main__":
        # Allow module to be run as script
        print("Running module as script")
        sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
        import crypto
    else:
        raise


class TestCreateKey(unittest.TestCase):
    """
    Tests that the create_key function does not error out.
    """
#    @classmethod
#    def setUpClass(cls):
    password = "secret".encode('utf-8')
    salt = "salt".encode('utf-8')
    key = b'P6CUIRwM8u0dMyq0OtxpqrRp8ODyyuY0XIG7h07vP54='

    def test_password_not_bytes_raises_error(self):
        with self.assertRaises(TypeError):
            crypto.create_key("non-bytes secret", self.salt)

    def test_salt_not_bytes_raises_error(self):
        with self.assertRaises(TypeError):
            crypto.create_key(self.password, "salt")

    def test_correct_key_generated(self):
        result = crypto.create_key(self.password, self.salt)
        self.assertEqual(result, self.key)


class TestEncodeAndPepperPW(unittest.TestCase):
    """

    """
    password = "mypass"
    pepper = "pepper"
    peppered = b'mypass\xf3J\xe6U\xf6mSpz\x01\x01\x1b\xcd\xe3\x89\xea'
    invalid_types = (
                     (1, 2),            # tuple
                     [3, 4],            # list
                     {"a": 1},          # dict
                     )

    def test_encode_and_pepper_pw(self):
        result = crypto.encode_and_pepper_pw(self.password)
        self.assertEqual(result, self.peppered)

    def test_encode_and_pepper_pw_with_custom_pepper(self):
        result = crypto.encode_and_pepper_pw(self.password, self.pepper)
        self.assertEqual(result, (self.password + self.pepper).encode('utf-8'))

    def test_raises_error_on_invalid_password_types(self):
        for pw in self.invalid_types:
            with self.subTest(pw=pw):
                with self.assertRaises(TypeError):
                    crypto.encode_and_pepper_pw(pw)

    def test_raises_error_on_invalid_pepper_types(self):
        for pepper in self.invalid_types:
            with self.subTest(pepper=pepper):
                with self.assertRaises(TypeError):
                    crypto.encode_and_pepper_pw(self.password, pepper)


class TestGetSalt(unittest.TestCase):
    """

    """
    def test_get_salt_no_error(self):
        try:
            crypto.get_salt()
        except Exception as err:
            self.fail("get_salt raised exception: {}".format(err))


class TestDeletePassword(unittest.TestCase):
    """
    """
    service = "PyBank_UnitTests"
    user = "test_runner"
    password = "secret"

    def setUp(self):
        crypto.create_password(self.password, self.service, self.user)

    def test_delete_password(self):
        try:
            crypto.delete_password(self.service, self.user),
        except keyring.errors.PasswordDeleteError:
            self.fail("Unable to delete password")

class TestCreatePassword(unittest.TestCase):
    """
    """
    service = "PyBank_UnitTests"
    user = "test_runner"
    password = "secret"

    def setUp(self):
        try:
            crypto.delete_password(self.service, self.user)
        except keyring.errors.PasswordDeleteError:
            pass

    def test_create_password(self):
        try:
            crypto.create_password(self.password, self.service, self.user),
        except keyring.errors.PasswordSetError:
            self.fail("Unable to set password")


class TestCheckPassword(unittest.TestCase):
    """
    """
    service = "PyBank_UnitTests"
    user = "test_runner"
    password = "secret"

    def setUp(self):
        try:
            crypto.delete_password(self.service, self.user)
        except keyring.errors.PasswordDeleteError:
            pass
        finally:
            crypto.create_password(self.password, self.service, self.user)

    def test_check_good_password(self):
        self.assertTrue(crypto.check_password("secret",
                                              self.service,
                                              self.user))

    def test_check_bad_password(self):
        self.assertFalse(crypto.check_password("aaa",
                                               self.service,
                                               self.user))


class TestGetPassword(unittest.TestCase):
    """
    """
    service = "PyBank_UnitTests"
    user = "test_runner"
    password = "secret"

    def setUp(self):
        try:
            crypto.delete_password(self.service, self.user)
        except keyring.errors.PasswordDeleteError:
            pass
        finally:
            crypto.create_password(self.password, self.service, self.user)


    def test_get_password(self):
        result = crypto.get_password(self.service, self.user)
        self.assertEqual(self.password, result)


class TestCheckPasswordExists(unittest.TestCase):
    """
    """
    service = "PyBank_UnitTests"
    user = "test_runner"
    password = "secret"

    def setUp(self):
        try:
            crypto.delete_password(self.service, self.user)
        except keyring.errors.PasswordDeleteError:
            pass
        finally:
            crypto.create_password(self.password, self.service, self.user)

    def test_check_password_does_exist(self):
        self.assertTrue(crypto.check_password_exists(self.service, self.user))

    def test_check_password_does_not_exists(self):
        self.assertFalse(crypto.check_password_exists("service", "some_user"))


class TestEncryptFile(unittest.TestCase):
    """
    """
    pass


class TestDecryptFile(unittest.TestCase):
    """
    """
    pass


class TestEncryptedRead(unittest.TestCase):
    """
    """
    pass


class TestEncryptedWrite(unittest.TestCase):
    """
    """
    pass


def main():
    """
    Main entry point
    """
    docopt(__doc__, version=__version__)    # TODO: pull VERSION from __init__
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
