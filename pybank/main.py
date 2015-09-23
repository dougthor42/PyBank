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
    # Imports used for unittests
    from . import pbsql
    from . import gui
    from . import crypto
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
        from __init__ import (__project_name__,
                              __version__,
                              )
        logging.debug("Imports for Spyder IDE")
    except ImportError:
         # Imports used by cx_freeze
        from pybank import pbsql
        from pybank import gui
        from pybank import crypto
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
def password_prompt_loop():
    # Password Prompt Loop
    logging.debug('Starting password prompt loop')
    while True:
        password = gui.password_prompt()
        if password is None:
            logging.debug('User canceled password prompt; exiting')
            return
        elif crypto.check_password(password):
            logging.debug('Password OK')
            break
        else:
            logging.debug('Invalid password')
            time.sleep(0.5)     # slow down brute-force attempts
            continue

def password_create_loop():
    # Password Prompt Loop
    logging.debug('Starting password prompt loop')
    while True:
        password = gui.password_prompt()
        if password is None:
            logging.debug('User canceled password prompt; exiting')
            return
        elif crypto.check_password(password):
            logging.debug('Password OK')
            break
        else:
            logging.debug('Invalid password')
            time.sleep(0.5)     # slow down brute-force attempts
            continue

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

    """
    docopt(__doc__, version=__version__)
    logging.debug("Running pybank.py")

    # Check if the database file exists
    database_file = 'PyBank.db'
    logging.debug('Checking for existing database: {}'.format(database_file))
    if not os.path.isfile(database_file):
        logging.debug('database file not found, will create')
        logging.debug('Prompting user to make a password')
        pw = gui.password_create()
        if pw is None:
            logging.debug('User canceled password creation; exiting')
            return
        crypto.create_password(pw)
        logging.debug('Creating database file')
#        pbsql.create_db(database_file)
    else:
        logging.debug('database file found')
        pw = password_prompt_loop()
        logging.debug('creating key')
#        key = crypto.create_key(pw)

        logging.debug('decrypting database')
        temp_file = 'temp.db'
#        crypto.decrypt_file(database_file, key, temp_file)

        logging.debug('copying db to memory')
        # magic

        logging.debug('deleting temporary db file')
#        os.remove(temp_file)

    logging.debug('starting gui')
    gui.MainApp()

    logging.debug("End")


if __name__ == "__main__":
    main()
