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
import unittest
import unittest.mock as mock
import os
import os.path as osp
import logging

# Third-Party
import keyring

# Package / Application
from .. import crypto


class TestCreateKey(unittest.TestCase):
    """
    Tests that the create_key function does not error out.
    """
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
    file = "temp.txt"
    encrypted_file = "temp.crypto"
    contents = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
    password = b"secret"
    salt = b"salt"

    @classmethod
    def setUpClass(cls):
        cls.key = crypto.create_key(cls.password, cls.salt)
        with open(cls.file, 'wb') as openf:
            openf.write(cls.contents)

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove(cls.file)
            os.remove(cls.encrypted_file)
        except OSError:
            pass

    def test_encrypt_file(self):
        try:
            crypto.encrypt_file(self.file, self.key)
        except Exception as err:
            self.fail("encrypt_file raised exception: {}".format(err))

    def test_encrypt_file_actually_encrypts(self):
        crypto.encrypt_file(self.file, self.key)
        with open(self.file, 'rb') as openf:
            result = openf.read()
        self.assertNotEqual(self.contents, result)

    def test_encrypt_file_with_copy_actually_encrypts(self):
        crypto.encrypt_file(self.file, self.key, copy=True)
        with open(self.encrypted_file, 'rb') as openf:
            result = openf.read()
        self.assertNotEqual(self.contents, result)


class TestDecryptFile(unittest.TestCase):
    """
    """
    file = "temp.txt"
    encrypted_file = "temp.crypto"
    contents = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
    password = b"secret"
    salt = b"salt"
    key = crypto.create_key(password, salt)

    @classmethod
    def setUpClass(cls):
        with open(cls.encrypted_file, 'wb') as openf:
            openf.write(cls.contents)
        crypto.encrypt_file(cls.encrypted_file, cls.key)

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove(cls.encrypted_file)
            os.remove(cls.file)
        except OSError:
            pass

#    def setUp(self):
#        self.

#    @unittest.skip("This is failing and it shouldn't be")
    def test_decrypt_file(self):
        try:
            crypto.decrypt_file(self.encrypted_file, self.key, self.file)
        except crypto.InvalidToken:
            self.fail("decrypt_file raised InvalidToken")

    def test_decrypt_file_with_new_file(self):
        with open(self.encrypted_file, 'rb') as openf:
            old_result = openf.read()
        crypto.decrypt_file(self.encrypted_file, self.key, new_file=self.file)
        with open(self.file, 'rb') as openf:
            new_result = openf.read()
        self.assertNotEqual(new_result, old_result)


class TestEncryptedRead(unittest.TestCase):
    """
    """
    file = "temp.txt"
    encrypted_file = "temp.crypto"
    contents = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
    password = b"secret"
    salt = b"salt"
    key = crypto.create_key(password, salt)

    @classmethod
    def setUpClass(cls):
        with open(cls.encrypted_file, 'wb') as openf:
            openf.write(cls.contents)
        crypto.encrypt_file(cls.encrypted_file, cls.key)

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove(cls.encrypted_file)
            os.remove(cls.file)
        except OSError:
            pass

    def test_encrypted_read(self):
        result = crypto.encrypted_read(self.encrypted_file, self.key)
        self.assertEqual(result, self.contents)


class TestEncryptedWrite(unittest.TestCase):
    """
    """
    file = "temp.txt"
    contents = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit"
    password = b"secret"
    salt = b"salt"
    key = crypto.create_key(password, salt)

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove(cls.file)
        except OSError:
            pass

    def test_encrypted_write(self):
        try:
            crypto.encrypted_write(self.file, self.key, self.contents)
        except Exception as err:
            self.fail("encrypted_write raised exception: {}".format(err))


class TestGetSalt_FileCreated(unittest.TestCase):
    """
    """
    file = "temp_salt.txt"

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        """ Remove the salt file created by get_salt """
        try:
            os.remove(cls.file)
        except OSError:
            pass

    def test_get_salt_creates_file(self):
        crypto.get_salt(self.file)
        self.assertTrue(os.path.exists(self.file))


class TestGetSalt_FilePopulated(unittest.TestCase):
    """
    """
    file = "temp_salt.txt"

    @classmethod
    def setUpClass(cls):
        """ Create the salt file so that we can read it in the test """
        crypto.get_salt(cls.file)

    @classmethod
    def tearDownClass(cls):
        """ Remove the salt file created by setUpClass """
        try:
            os.remove(cls.file)
        except OSError:
            pass

    def test_get_salt_populates_file(self):
        result = crypto.get_salt(self.file)
        self.assertEqual(len(result), 32)


class TestGetSalt_FileExists(unittest.TestCase):
    """
    """
    file = "temp_salt.txt"
    salt = b"salt"

    @classmethod
    def setUpClass(cls):
        """ Create a dummy salt file before running the test """
        with open(cls.file, 'wb') as openf:
            openf.write(cls.salt)

    @classmethod
    def tearDownClass(cls):
        """ Remove the dummy salt file after running the test """
        try:
            os.remove(cls.file)
        except OSError:
            pass

    def test_get_salt_file_already_exists(self):
        result = crypto.get_salt(self.file)
        self.assertEqual(result, self.salt)
