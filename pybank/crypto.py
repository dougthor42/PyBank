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
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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
    with open(file, 'rb') as openf:
        data = openf.read()

    f = Fernet(key)

#    return io.BytesIO(f.decrypt(data))
#    return f.decrypt(data)

    a = time.perf_counter()
    d = f.decrypt(data)
    b = time.perf_counter()
    print("decryption took {}s".format(b-a))
    return d


def encrypted_write(file, key, data):
    """ Writes to an encrypted file """

    f = Fernet(key)
    a = time.perf_counter()
    encrypted_data = f.encrypt(data)
    b = time.perf_counter()
    print("encryption took {}s".format(b-a))

    with open(file, 'wb') as openf:
        openf.write(encrypted_data)

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
    """ Decrypts a given file """
    if new_file is None:
        new_file = "decrypted_" + file

    with open(new_file, 'wb') as openf:
        openf.write(encrypted_read(file, key))

    return new_file


def check_password(password):
    """ Checks a password against the keyring """
    password = password.encode('utf-8')
    service = 'PyBank'
    user = 'user'
    return password == keyring.get_password(service, user).encode('utf-8')


def create_password(password):
    """ Creates a new password for PyBank in the keyring """
    service = "PyBank"
    user = 'user'
    keyring.set_password(service, user, password)


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
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=32,
                     salt=salt,
                     iterations=100000,
                     backend=default_backend()
                     )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key



def main():
#    # Read or create salt file.         # XXX: Put in config file?
    salt_file = "salt.txt"
    if not os.path.exists(salt_file):
        with open(salt_file, 'wb') as openf:
            salt = os.urandom(32)
            openf.write(salt)
    else:
        with open(salt_file, 'rb') as openf:
            salt = openf.read()

    print("Salt is:\n{}".format(salt))

#    # Prompt the user for a password
#    pw_input = input("type in the password 'secret'  >> ")
#    password = keyring.get_password('PyBank', 'user').encode('utf-8')
#    if password != pw_input.encode('utf-8'):
#        raise Exception("I said type in 'secret'!")
#
#    # Add a pepper. Not really useful since this is open-source, but /shrug.
#    # TODO: look into alternate pepper solution
#    #       - perhaps unique to the computer it's running on?
#    #         - But what if the user wants to change computers...
#    #       - secondary password?
    password = 'pybank'.encode('utf-8')
    password += b'\xf3J\xe6U\xf6mSpz\x01\x01\x1b\xcd\xe3\x89\xea'
#
    key = create_key(password, salt)
#
#    # Encrypt or Decrypt the file.
#    print("Encrypting encrypted file: PyBank.db")
#    encrypt_file("PyBank.db", key)
#
##    input("Press enter to read the encrypted file.")
#    print("Decrypting file")
#    a = encrypted_read("crypto_PyBank.db", key)


    # Since I can't read/write directly to the encrypted database,
    # and I can't open a database from a BytesIO stream, I've decided
    # to do the following:
    # ===== UPDATE 2015-11-24: no longer doing this. See below =====
    # 1.  decrypt the DB once to a temporary file
    # 2.  copy it to a memory db (http://stackoverflow.com/a/4019182/1354930)
    # 3.  Remove temporary file.
    # This will minimize the amount of time that the file is not encrypted.

    # =======================================================================
    # Update 2015-11-24: instead of decrypting to a temp file, let's save
    # the SQLite dump string. I can encrypt and decrypt that before saving
    # anywhere, and this database should stay relatively small (< 50k lines)
    # so I *think* it will be quick...
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

    file_db = sqlite3.connect("test_database_large.db")
    a = time.perf_counter()
    dump = "".join(line for line in file_db.iterdump())
    b = time.perf_counter()
    print("iterdump took {}s".format(b-a))
    dump = dump.encode('utf-8')
    encrypted_write("test_database_large_dump_encrypted.txt", key, dump)
#    with open("test_database_dump.txt", "w") as openf:
#        openf.write(dump)

    new_dump = encrypted_read("test_database_large_dump_encrypted.txt", key)
    new_dump = new_dump.decode('utf-8')
    with open("test_database_dump_2.txt", "w") as openf:
        openf.write(new_dump)

    main_db = sqlite3.connect(":memory:")
    a = time.perf_counter()
    main_db.executescript(new_dump)
    b = time.perf_counter()
    print("dbwrite took {}s".format(b-a))
    cursor = main_db.cursor()
    cursor.execute("SELECT * FROM acct")
    data = cursor.fetchall()
    print()
    print()
    print(data)


if __name__ == "__main__":
    main()

