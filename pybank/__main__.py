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
    from . import (__project_name__,
                   __version__,
                   __released__,
                   )
    from . import gui
    from . import gui_utils
    from . import crypto
    from . import utils
    from . import orm
    from . import constants
    logging.debug("Imports for main.py complete (Method: UnitTest)")
except SystemError:
    try:
        # Imports used by Spyder
        from __init__ import (__project_name__,
                              __version__,
                              __released__,
                              )
        import gui
        import crypto
        import utils
        import gui_utils
        import orm
        import constants
        logging.debug("Imports for main.py complete (Method: Spyder IDE)")
    except ImportError:
         # Imports used by cx_freeze
        from pybank import (__project_name__,
                            __version__,
                            __released__,
                            )
        from pybank import gui
        from pybank import crypto
        from pybank import utils
        from pybank import gui_utils
        from pybank import orm
        from pybank import constants
        logging.debug("Imports for main.py complete (Method: Executable)")


# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------
PYBANK_FILE = constants.PYBANK_FILE
SALT_FILE = constants.SALT_FILE

# ---------------------------------------------------------------------------
### Classes
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
### Functions
# ---------------------------------------------------------------------------
@utils.logged
def create_new(db_file):
    """
    """
    logging.debug('database file not found, an empty one will be created')
    logging.debug('Prompting user to make a password')
    if not gui_utils.create_pw():   # Use pw = 'pybank' for testing
        logging.debug('User canceled password creation; exiting')
        raise RuntimeError

    key = crypto.get_key()

    logging.debug('Creating database file')
    # 1. Create the DB and dump it
    dump = list(orm.sqlite_iterdump(orm.engine, orm.session))
    dump = "".join(line for line in dump)
    dump = dump.encode('utf-8')
    # 2. Save the dump to an encrypted file.
    crypto.encrypted_write(db_file, key, dump)


@utils.logged
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
    msg = "Starting %s v%s, released %s"
    logging.info(msg, __project_name__, __version__, __released__)
    logging.info("End of %s program.", __project_name__)

    docopt(__doc__, version=__version__)

    # Check if the database file exists
    database_file = utils.find_data_file(PYBANK_FILE)
    logging.info('Checking for existing database: {}'.format(database_file))
    if not os.path.isfile(database_file):
        logging.warning("database file not found. Creating.")
        try:
            create_new(database_file)
        except RuntimeError:
            # User canceled the creation process, we need to exit.
            return
    else:
        logging.info('database file found')
        if not gui_utils.prompt_pw():
            logging.debug('User canceled password prompt; exiting')
            return
        logging.debug('creating key')

        key = crypto.get_key()

        logging.debug('decrypting database')
        new_dump = crypto.encrypted_read(database_file, key)
        new_dump = new_dump.decode('utf-8').split(";")

        logging.debug('copying db to memory')
        logging.debug('creating database structure')
        logging.debug('starting copy')
        orm.copy_to_sa(orm.engine, orm.session, new_dump)



    logging.debug('starting gui')
    gui.MainApp()

    logging.info("End")


if __name__ == "__main__":
    main()
