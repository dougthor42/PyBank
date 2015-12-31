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
# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
import os
import logging
import base64
import io
import sqlite3
import time

# Third Party
import keyring
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidKey

# Package / Application
try:
    # Imports used for unittests
    from . import pbsql
#    from . import plots
#    from . import utils
#    from . import (__project_name__,
#                   __version__,
#                   )
    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
        import pbsql
#        import plots
#        import utils
#        from __init__ import (__project_name__,
#                              __version__,
#                              )
        logging.debug("Imports for Spyder IDE")
    except ImportError:
         # Imports used by cx_freeze
        from pybank import pbsql
#        from pybank import plots
#        from pybank import utils
#        from pybank import (__project_name__,
#                            __version__,
#                            )
        logging.debug("imports for Executable")


# TODO: Once pysqlcipher gets to python3, switch to that.
#       Actually, not really. I like my solution of saving the encrypted txt.

# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
### Classes
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
### Functions
# ---------------------------------------------------------------------------
def encrypted_read(file, key):
    """ Reads an encrypted file """
    logging.debug("opening encrypted file `{}`".format(file))
    with open(file, 'rb') as openf:
        data = openf.read()

    f = Fernet(key)

#    return io.BytesIO(f.decrypt(data))
#    return f.decrypt(data)

    logging.debug("decrypting...")
    try:
        d = f.decrypt(data)
    except InvalidToken:
        logging.critical("Key Mismatch with file! Unable to decrypt!")
        raise

    logging.debug("decryption complete")
    return d


def encrypted_write(file, key, data):
    """ Writes to an encrypted file """
    logging.debug("writing encrypted file `{}`".format(file))
    f = Fernet(key)
    logging.debug("encrypting...")
    encrypted_data = f.encrypt(data)
    logging.debug("encryption complete ")

    logging.debug("writing encrypted data")
    with open(file, 'wb') as openf:
        openf.write(encrypted_data)
    logging.debug("complete")
    return


def encrypt_file(file, key, copy=False):
    """
    Encrypts a given file.

    If copy is True, creates a copy of the file with a .crypto extension
    """
    # First we need to read in the file's contents
    with open(file, 'rb') as openf:
        decrypted_data = openf.read()

    encrypted_write("crypto_" + file, key, decrypted_data)

    return


def decrypt_file(file, key, new_file=None):
    """ Decrypts a given file, saving it as a new, unencrypted file. """
    if new_file is None:
        new_file = "decrypted_" + file

    with open(new_file, 'wb') as openf:
        openf.write(encrypted_read(file, key))

    return new_file


def get_password(service="Pybank", user="user"):
    return keyring.get_password(service, user)


def check_password(password, service="Pybank", user="user"):
    """ Checks a password against the keyring """
    password = password.encode('utf-8')
    pw = get_password(service, user).encode('utf-8')
    return password == pw


def create_password(password, service="Pybank", user="user"):
    """ Creates a new password for PyBank in the keyring """
    keyring.set_password(service, user, password)
    return


def check_password_exists(service="Pybank", user="user"):
    """ Verify that a password for PyBank exists in the keyring """
    return bool(keyring.get_password(service, user))


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
    logging.debug("creating key")
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=32,
                     salt=salt,
                     iterations=100000,
                     backend=default_backend()
                     )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def get_key():
    """ Creates and returns the encryption key. """
    salt = get_salt()
    pw = get_password()
    peppered_pw = encode_and_pepper_pw(pw)
    key = create_key(peppered_pw, salt)

    return key


def get_salt(file="salt.txt"):
    """ Reads the salt file if it exists. Otherwise, creates it. """
    logging.debug("getting salt...")
    if not os.path.exists(file):
        logging.debug("salt file DNE - creating")
        with open(file, 'wb') as openf:
            salt = os.urandom(32)
            openf.write(salt)
    else:
        logging.debug("salt file found")
        with open(file, 'rb') as openf:
            salt = openf.read()

    return salt


def encode_and_pepper_pw(string):
    """ Encodes a string as binary and adds a pepper """
    logging.debug("encoding and peppering string")
    string = string.encode('utf-8')
    string += b'\xf3J\xe6U\xf6mSpz\x01\x01\x1b\xcd\xe3\x89\xea'
    return string


def main():
#    # Read or create salt file.         # XXX: Put in config file?
    salt = get_salt()
#    print("Salt is:\n{}".format(salt))

#    # Add a pepper. Not really useful since this is open-source, but /shrug.
#    # TODO: look into alternate pepper solution
#    #       - perhaps unique to the computer it's running on?
#    #         - But what if the user wants to change computers...
#    #       - secondary password?
    password = encode_and_pepper_pw('pybank')
    key = create_key(password, salt)

    # 1.  decrypt the DB once to a temporary file
    # 2.  copy it to a memory db (http://stackoverflow.com/a/4019182/1354930)
    # 3.  Remove temporary file.
    # This will minimize the amount of time that the file is not encrypted.

    # =======================================================================
    # Instead of decrypting to a temp file, let's save the SQLite dump string.
    # I can encrypt and decrypt that before saving anywhere, and this database
    # should stay relatively small (< 50k lines) so it should be quick...
    #
    # First-order benchmarks
    #              Database          Times           File Size
    # Lines     Dump   write    Encrypt  Decrypt   DB       Encrypted Text
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

    file_db = sqlite3.connect("test_database.db")
    dump = "".join(line for line in file_db.iterdump())
    dump = dump.encode('utf-8')
    encrypted_write("test_database.pybank", key, dump)
#    with open("test_database_dump.txt", "w") as openf:
#        openf.write(dump)

    new_dump = encrypted_read("test_database.pybank", key)
    new_dump = new_dump.decode('utf-8')

    # copy to an im-memory database
    main_db = sqlite3.connect(":memory:")
    main_db.executescript(new_dump)

    # check that it worked.
    cursor = main_db.cursor()
    cursor.execute("SELECT * FROM sqlite_sequence")
    data = cursor.fetchall()
    print()
    print()
    time.sleep(0.2)
    print(data)


if __name__ == "__main__":
#    main()
    check_password_exists()

