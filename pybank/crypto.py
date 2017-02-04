# -*- coding: utf-8 -*-
"""
Cryptography components of PyBank

Created on Tue Sep 15 16:06:32 2015

Usage:
    crypto.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""
    # Add a pepper. Not really useful since this is open-source, but /shrug.
    # TODO: look into alternate pepper solution
    #       - perhaps unique to the computer it's running on?
    #         - But what if the user wants to change computers...
    #       - secondary password?

    # =======================================================================
    # Instead of decrypting to a temp file, let's save the SQLite dump string.
    # I can encrypt and decrypt that before saving anywhere, and this database
    # should stay relatively small (< 50k lines) so it should be quick...
    #
    # First-order benchmarks
    #              Database          Times           File Size
    # Rows      Dump   write    Encrypt  Decrypt   DB       Encrypted Text
    # 10        3.8ms  3ms      550us    312us     36kB     13kB
    # 10k       57ms   16ms     29ms     25.5ms    529kB    1206kB
    # 50k       295ms  788ms    72ms     65ms      5.3MB    6MB
    # =======================================================================

    # NOTE: Secure delete using Gutmann method? (if needed)
    #       https://en.wikipedia.org/wiki/Gutmann_method
    #       Not needed because I'm no longer deleting anything and most
    #       hard drives are starting to become solid state anyway... this
    #       method is for magnetic platter storage

    # TODO: Get security review by someone else.

# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
import os
import logging
import base64
import os.path

# Third Party
import keyring
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidKey

# Package / Application
from . import constants
from . import utils


# TODO: Once pysqlcipher gets to python3, switch to that.
#       Actually, not really. I like my solution of saving the encrypted txt.

# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------
SERVICE = "Pybank"
USER = "user"
SALT_FILE = constants.SALT_FILE

# ---------------------------------------------------------------------------
### Classes
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
### Functions
# ---------------------------------------------------------------------------
@utils.logged
def encrypted_read(file, key):
    """ Reads an encrypted file """
    logging.info("opening encrypted file `{}`".format(file))
    with open(file, 'rb') as openf:
        data = openf.read()

    f = Fernet(key)

#    return io.BytesIO(f.decrypt(data))
#    return f.decrypt(data)

    logging.debug("decrypting...")
    try:
        d = f.decrypt(data)
        logging.debug("decryption complete")
    except InvalidToken:
        logging.exception("Key Mismatch with file! Unable to decrypt!")
        raise

    return d


@utils.logged
def encrypted_write(file, key, data):
    """ Writes to an encrypted file """
    logging.info("writing encrypted file `{}`".format(file))
    f = Fernet(key)
    logging.debug("encrypting...")
    encrypted_data = f.encrypt(data)
    logging.debug("encryption complete ")

    logging.debug("writing encrypted data")
    with open(file, 'wb') as openf:
        openf.write(encrypted_data)
    logging.debug("complete")
    return


@utils.logged
def encrypt_file(file, key, copy=False):
    """
    Encrypts a given file.

    If copy is True, creates a copy of the file with a .crypto extension
    """
    # First we need to read in the file's contents
    with open(file, 'rb') as openf:
        decrypted_data = openf.read()

    if copy:
        fn = os.path.splitext(file)[0]
        fn += ".crypto"
        encrypted_write(fn, key, decrypted_data)
    else:
        encrypted_write(file, key, decrypted_data)

    return


@utils.logged
def decrypt_file(file, key, new_file=None):
    """
    Decrypts a given file, overwriting the original unless
    new_file is given.
    """
    if new_file is None:
        new_file = file

    with open(new_file, 'wb') as openf:
        openf.write(encrypted_read(file, key))

    return


@utils.logged
def get_password(service=SERVICE, user=USER):
    return keyring.get_password(service, user)


@utils.logged
def check_password(password, service=SERVICE, user=USER):
    """ Checks a password against the keyring """
    password = password.encode('utf-8')
    pw = get_password(service, user).encode('utf-8')
    return password == pw


@utils.logged
def create_password(password, service=SERVICE, user=USER):
    """ Creates a new password for PyBank in the keyring """
    keyring.set_password(service, user, password)
    return


@utils.logged
def check_password_exists(service=SERVICE, user=USER):
    """ Verify that a password for PyBank exists in the keyring """
    return bool(keyring.get_password(service, user))


@utils.logged
def delete_password(service=SERVICE, user=USER):
    """ Delete a password from the keyring """
    keyring.delete_password(service, user)


@utils.logged
def create_key(password, salt):
    """
    Create a Fernet key from a (peppered) password and salt.

    Uses the PBKDF2HMAC key-derivation function.

    Parameters:
    -----------
    password : bytes
        The password to use as the base of the key derivation function. This
        should be peppered.

    salt : bytes
        A salt to use. This should be 16 bytes minimum, 32 or 64 preferred.

    Returns:
    --------
    key : bytes
        A URL-safe base64-encoded 32-byte key. This **must** be kept secret.

    Notes:
    ------
    See:

    + https://cryptography.io/en/latest/fernet
    + https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
    + kdf: Key Derivation Function
    + PBKDF2HMAC: Password-Based Key Derivation Function 2, Hash-based
      Message Authentication Code

    """
    logging.info("Creating encryption key")
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=32,
                     salt=salt,
                     iterations=100000,
                     backend=default_backend()
                     )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


@utils.logged
def get_key(service=SERVICE, user=USER):
    """ Creates and returns the encryption key. """
    logging.info("Getting key")
    salt = get_salt()
    pw = get_password(service, user)
    peppered_pw = encode_and_pepper_pw(pw)
    key = create_key(peppered_pw, salt)

    return key


@utils.logged
def get_salt(file=SALT_FILE):
    """ Reads the salt file if it exists. Otherwise, creates it. """
    logging.info("Getting or creating salt string.")
    if not os.path.exists(file):
        logging.warning("salt file DNE - creating")
        with open(file, 'wb') as openf:
            salt = os.urandom(32)
            openf.write(salt)
    else:
        with open(file, 'rb') as openf:
            salt = openf.read()

    return salt


@utils.logged
def encode_and_pepper_pw(string, pepper=None):
    """ Encodes a string as binary and adds a pepper """
    logging.info("Encoding and peppering string")
    if pepper is None:
        pepper = b'\xf3J\xe6U\xf6mSpz\x01\x01\x1b\xcd\xe3\x89\xea'

    try:
        string = string.encode('utf-8')
        logging.warning("Password string was not encoded as utf-8")
    except AttributeError:
        # string is already encoded
        pass

    try:
        pepper = pepper.encode('utf-8')
        logging.warning("Pepper string was not encoded as utf-8")
    except AttributeError:
        # pepper is already encoded
        pass

    return string + pepper


if __name__ == "__main__":
    pass

