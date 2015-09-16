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
import logging

# Third Party
from cryptography.fernet import Fernet
import keyring

# Package / Application
try:
    # Imports used for unittests
#    from . import pbsql
#    from . import plots
#    from . import utils
#    from . import __init__ as __pybank_init
#    from . import (__project_name__,
#                   __version__,
#                   )
    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
#        import pbsql
#        import plots
#        import utils
#        import __init__ as __pybank_init
#        from __init__ import (__project_name__,
#                              __version__,
#                              )
        logging.debug("Imports for Spyder IDE")
    except ImportError:
         # Imports used by cx_freeze
#        from pybank import pbsql
#        from pybank import plots
#        from pybank import utils
#        from pybank import __init__ as __pybank_init
#        from pybank import (__project_name__,
#                            __version__,
#                            )
        logging.debug("imports for Executable")


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
    decrypted_data = f.decrypt(data)

    return decrypted_data


def encrypted_write(file, key, data):
    """ Writes to an encrypted file """

    f = Fernet(key)
    encrypted_data = f.encrypt(data)

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
        unencrypted_data = openf.read()

    encrypted_write("crypto_" + file, key, unencrypted_data)

    return


def decrypt_file(file, key, new_file=None):
    """ Decrypts a given file """
    new_file = "decrypted_" + file


    with open(new_file, 'wb') as openf:
        openf.write(encrypted_read(file, key))

    return


def main():
    print("====================")
    print("Creating Key:")
    key = Fernet.generate_key()
    print(key)

    print("Encrypting encrypted file: PyBank.db")
    encrypt_file("PyBank.db", key)

    input("Press enter to read the encrypted file.")
    print("Decrypting file")
    decrypt_file("crypto_PyBank.db", key)


if __name__ == "__main__":
    main()
