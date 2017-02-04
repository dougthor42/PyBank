# -*- coding: utf-8 -*-
"""
PyBank
============

This program is supposed to be a tracker for finances and money.

Basic Goals:
------------

1.  Able to download transactions via OFX
2.  Save transaction register to a local encrypted database
3.  Able to plot funds vs time.
4.  List transactions in a register-like GUI, similar to Quicken

Notes:
------
I may have to re-write an OFX parser...

Transaction matching and download start date = previous download date.

# TODO: Do I want to name transaction tables as transaction_0 or
        transaction_00? Or even transaction_000?
# TODO: Does Google Wallet have OFX?
"""
### Imports #################################################################
# Standard Library
import logging
import os.path

# Third Party

# Package / Application
from . import _logging
from pybank.__about__ import *      # OK because I define __all__


### Package Constants #######################################################
_logging._setup_logging()

PROGRAM_DIR= os.path.dirname(os.path.abspath(__file__))
logging.info("Program directory: %s", PROGRAM_DIR)
