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
#    from . import pbsql
    from . import gui
    from . import gui_utils
    from . import crypto
    from . import utils
    from . import sa_orm_base as base
    from . import sa_orm_transactions
    from . import (__project_name__,
                   __version__,
                   __released__,
                   )
    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
#        import pbsql
        import gui
        import crypto
        import utils
        import gui_utils
        import sa_orm_base as base
        import sa_orm_transactions
        from __init__ import (__project_name__,
                              __version__,
                              __released__,
                              )
        logging.debug("Imports for Spyder IDE")
    except ImportError:
         # Imports used by cx_freeze
#        from pybank import pbsql
        from pybank import gui
        from pybank import crypto
        from pybank import utils
        from pybank import gui_utils
        from pybank import sa_orm_base as base
        from pybank import sa_orm_transactions
        from pybank import (__project_name__,
                            __version__,
                            __released__,
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
    if not gui_utils.create_pw():   # Use pw = 'pybank' for testing
        logging.debug('User canceled password creation; exiting')
        return    # this needs to return outside the if statement

    salt = crypto.get_salt()
    pw = crypto.get_password()
    peppered_pw = crypto.encode_and_pepper_pw(pw)
    key = crypto.create_key(peppered_pw, salt)

    crypto.create_password(pw)
    logging.debug('Creating database file')
    # 1. Create an unencrypted file based on the template
#        db = pbsql.create_db_sa(":memory:")
#    db = pbsql.create_db(":memory:")
#    engine, session = base.create_database()
    # 2. Dump it, encrypt the dump, and then save the encrypted dump.
    # Move to pbsql module
    dump = list(sa_orm_transactions.sqlite_iterdump(base.engine, base.session))
    dump = "".join(line for line in dump)
    dump = dump.encode('utf-8')
#    dump = "".join(line for line in db.iterdump())
#    dump = dump.encode('utf-8')
    # 3. Encrypt the dump amd save it to a file
    crypto.encrypted_write(db_file, key, dump)


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
        pw = crypto.get_password()
        peppered_pw = crypto.encode_and_pepper_pw(pw)
        key = crypto.create_key(peppered_pw, salt)

        logging.debug('decrypting database')
        new_dump = crypto.encrypted_read(db_file, key)
        new_dump = new_dump.decode('utf-8').split(";")
#        print(new_dump)
#        print(type(new_dump))
#        return

        logging.debug('copying db to memory')
#        db = pbsql.create_db(":memory:")
        logging.debug('creating database structure')
#        engine, session = base.create_database()
        logging.debug('starting copy')
        sa_orm_transactions.copy_to_sa(base.engine, base.session, new_dump)
#        db.executescript(new_dump)

        # this db object needs to be sent around everywhere.


    logging.debug('starting gui')
    gui.MainApp()

    logging.debug("End")


if __name__ == "__main__":
    msg = "Starting %s v%s, released %s"
    logging.info(msg, __project_name__, __version__, __released__)
    main()

