# -*- coding: utf-8 -*-
"""
PyBank core module and main entry point.

Created on Mon May 25 15:57:10 2015

@author: dthor

Usage:
    oxf.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""

# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
import sys
import logging
import os.path
import time

# Third-Party
from docopt import docopt

# Package / Application
try:
    # Imports used by unit test runners
    from . import pbsql
    from . import gui
    from . import gui_utils
    from . import crypto
    from . import utils
    from . import (__project_name__,
                   __version__,
                   )
    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
        import pbsql
        import gui
        import crypto
        import utils
        import gui_utils
        from __init__ import (__project_name__,
                              __version__,
                              )
        logging.debug("Imports for Spyder IDE")
    except ImportError:
         # Imports used by cx_freeze
        from pybank import pbsql
        from pybank import gui
        from pybank import crypto
        from pybank import utils
        from pybank import gui_utils
        from pybank import (__project_name__,
                            __version__,
                            )
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
def nothing():
    """
    what if, instead of trying to encrypt and decrypt the sqlite file itself,
    I encrypt and decrypt the SQLite dump string... Then I could intercept
    and encrypt the string before it gets written to disk...
    +
    """
    pass


def create_new(db_file):
    """
    """
    logging.debug('database file not found, an empty one will be created')
    logging.debug('Prompting user to make a password')
    if not gui_utils.password_create():   # Use pw = 'pybank' for testing
        logging.debug('User canceled password creation; exiting')
        return    # this needs to return outside the if statement

    salt = crypto.get_salt()
    pw = crypto.encode_and_pepper_pw(crypto.get_password())
    key = crypto.create_key(pw, salt)

    crypto.create_password(pw)
    logging.debug('Creating database file')
    # 1. Create an unencrypted file based on the template
#        db = pbsql.create_db_sa(":memory:")
    db = pbsql.create_db(":memory:")
    # 2. Dump it, encrypt the dump, and then save the encrypted dump.
    # Move to pbsql module
    dump = "".join(line for line in db.iterdump())
    dump = dump.encode('utf-8')
    # 3. Encrypt the dump amd save it to a file
    crypto.encrypted_write(db_file, key, dump)


def dump_to_memory():
    """ """



def main():
    """
    Main entry point

    Flow:
    + Check for database file
      + if doesn't exist, create file and password. Encrypt file.
    + Ask for password
    + If dbfile didn't exists, create and encrypt
    + Decrypt file to local copy
    + copy to memory database
    + delete local copy
    + Gui loop
    + Auto-save loop
      + every 2 minutes, copy DB to file, encrypt it.

    """
    docopt(__doc__, version=__version__)
    logging.debug("Running pybank.py")

    db_file = 'test_database.pybank'

    # Check if the database file exists
    database_file = utils.find_data_file(db_file)
    logging.debug('Checking for existing database: {}'.format(db_file))
    if not os.path.isfile(database_file):
        create_new(db_file)
    else:
        logging.debug('database file found')
        if not gui_utils.prompt_pw():
            logging.debug('User canceled password prompt; exiting')
            return
        logging.debug('creating key')

        salt = crypto.get_salt()
        pw = crypto.encode_and_pepper_pw(crypto.get_password())
        key = crypto.create_key(pw, salt)

        logging.debug('decrypting database')
        new_dump = crypto.encrypted_read(db_file, key)
        print(new_dump)
        new_dump = new_dump.decode('utf-8')

        logging.debug('copying db to memory')
        db = pbsql.create_db(":memory:")
        db.executescript(new_dump)

        # this db object needs to be sent around everywhere.


    logging.debug('starting gui')
    gui.MainApp()

    logging.debug("End")


if __name__ == "__main__":
    main()

