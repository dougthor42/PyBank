# -*- coding: utf-8 -*-
"""
Holds the default values for constants use by PyBank.
"""
### Imports #################################################################
# Standard Library
import os.path

# Third Party
from wx import Colour

## Package / Application
from pybank import PROGRAM_DIR


LEDGER_COLOR_1 = Colour(255, 255, 255, 255)
LEDGER_COLOR_2 = Colour(255, 255, 204, 255)

DECIMAL_MARK = "."
THOUSANDS_SEP = ","
CURRENCY_SYM = "$"
TRAILING_CURRENCY_SYM = ""

PYBANK_FILE = os.path.join(PROGRAM_DIR, 'test_database.pybank')
SALT_FILE = os.path.join(PROGRAM_DIR, 'salt.txt')