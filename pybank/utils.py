# -*- coding: utf-8 -*-
"""
Various utilities used by PyBank.

Created on Tue May 12 13:30:56 2015

Usage:
    utils.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.
"""
# Standard Library
#import sys
#import os.path as osp
import logging

# Third-Party
from docopt import docopt

# Package / Application
try:
    # Imports used for unittests
    from . import __init__ as __pybank_init
#    from . import pbsql
    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
        import __init__ as __pybank_init
#        import pbsql
        logging.debug("Imports for Spyder IDE")
    except ImportError:
         # Imports used by cx_freeze
        from pybank import __init__ as __pybank_init
#        from pybank import pbsql
        logging.debug("imports for Executable")


def main():
    """
    Main entry point
    """
    docopt(__doc__, version=__pybank_init.__version__)
    print("Running utils.py")

    logging.debug("debugging")
#    logging.info("Info!")
#    logging.warn("warn: you should do this instead")
#    logging.warning("warning: you can't do anything about this")
#    logging.error("error")
#    logging.critical("critical")
#    logging.exception("exception")

    print("End")


if __name__ == "__main__":
    main()
