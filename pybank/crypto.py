# -*- coding: utf-8 -*-
"""
Cryptography components of PyBank.
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
    """
    Read an encrypted file.

    Parameters
    ----------
    file : str
    key : str

    Returns
    -------
    d : bytes
        The decrypted data.
    """
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
    """
    Write to an encrypted file.

    Parameters
    ----------
    file : str
    key : str
    data : bytes

    Returns
    -------
    None
    """
    logging.info("writing encrypted file `{}`".format(file))
    f = Fernet(key)
    logging.debug("encrypting...")
    encrypted_data = f.encrypt(data)
    logging.debug("encryption complete ")

    logging.debug("writing encrypted data")
    with open(file, 'wb') as openf:
        openf.write(encrypted_data)
    logging.debug("complete")


@utils.logged
def encrypt_file(file, key, copy=False):
    """
    Encrypt a given file.

    Parameters
    ----------
    file : str
        The file to encrypt.
    key : str
        The key to use for encryption.
    copy : bool, optional
        If True, create a copy of the file with a ``.crypto`` extension
        rather than overwriting ``file``.

    Returns
    -------
    None
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


@utils.logged
def decrypt_file(file, key, new_file=None):
    """
    Decrypt a given file, overwriting the original unless new_file is given.

    Parameters
    ----------
    file : str
        The file to decrypt
    key : str
        The key to use for decryption
    new_file : str, optional
        If not ``None``, then saves the decrypted ``file`` to ``new_file``.

    Returns
    -------
    None
    """
    if new_file is None:
        new_file = file

    with open(new_file, 'wb') as openf:
        openf.write(encrypted_read(file, key))


@utils.logged
def get_password(service=SERVICE, user=USER):
    """
    Get the user's password from the keyring.

    Parameters
    ----------
    service : str
        The service to get a password for.
    user : str
        The user to get a password for.

    Returns
    -------
    password : str
    """
    return keyring.get_password(service, user)


@utils.logged
def check_password(password, service=SERVICE, user=USER):
    """
    Check a password against the keyring.

    Parameters
    ----------
    password : str
        The password the check.
    service : str
        The service to get a password for.
    user : str
        The user to get a password for.

    Returns
    -------
    bool
        ``True`` if passwords match, otherwise ``False``.
    """
    password = password.encode('utf-8')
    pw = get_password(service, user).encode('utf-8')
    return password == pw


@utils.logged
def create_password(password, service=SERVICE, user=USER):
    """
    Create a new password for PyBank in the keyring.

    Parameters
    ----------
    password : str
        The password the check.
    service : str
        The service to get a password for.
    user : str
        The user to get a password for.

    Returns
    -------
    None
    """
    keyring.set_password(service, user, password)
    return


@utils.logged
def check_password_exists(service=SERVICE, user=USER):
    """
    Verify that a password for PyBank exists in the keyring.

    Parameters
    ----------
    service : str
        The service to get a password for.
    user : str
        The user to get a password for.

    Returns
    -------
    bool
        ``True`` if the password exists, otherwise ``False``.
    """
    return bool(keyring.get_password(service, user))


@utils.logged
def delete_password(service=SERVICE, user=USER):
    """
    Delete a password from the keyring.

    Parameters
    ----------
    service : str
        The service to get a password for.
    user : str
        The user to get a password for.

    Returns
    -------
    None
    """
    keyring.delete_password(service, user)


@utils.logged
def create_key(password, salt):
    """
    Create a Fernet key from a (peppered) password and salt.

    Uses the PBKDF2HMAC key-derivation function.

    Parameters
    ----------
    password : bytes
        The password to use as the base of the key derivation function. This
        should be peppered.

    salt : bytes
        A salt to use. This should be 16 bytes minimum, 32 or 64 preferred.

    Returns
    -------
    key : bytes
        A URL-safe base64-encoded 32-byte key. This **must** be kept secret.

    Notes
    -----
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
    """
    Create and return the encryption key.

    Parameters
    ----------
    service : str
        The service to get a password for.
    user : str
        The user to get a password for.

    Returns
    -------
    key : str
        The encryption key.
    """
    logging.info("Getting key")
    salt = get_salt()
    pw = get_password(service, user)
    peppered_pw = encode_and_pepper_pw(pw)
    key = create_key(peppered_pw, salt)

    return key


@utils.logged
def get_salt(file=SALT_FILE):
    """
    Read the salt file if it exists. Otherwise, creates it.

    Parameters
    ----------
    file : str
        The file that contains the salt string.

    Returns
    -------
    salt : str
        The read (or generated) salt.
    """
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
    """
    Encode a string as binary and adds a pepper.

    Parameters
    ----------
    string : str
    pepper : str, optional
        If None, use a fixed pepper listed below.

    Returns
    -------
    string : bytes
    """
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

