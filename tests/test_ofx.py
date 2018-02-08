# -*- coding: utf-8 -*-
"""
Tests OFX components.

Created on Tue May 12 13:31:46 2015

Usage:
    test_ofx.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""

# Standard Library
import datetime as dt

# Third-Party
import pytest

# Package / Application
from pybank import ofx


class TestFormatDate(object):
    
    def test_format_date(self):
        date = dt.date(2017, 1, 30)
        assert ofx.format_date(date) == "20170130"
        date = dt.date(2020, 12, 1)
        assert ofx.format_date(date) == "20201201"
        date = dt.date(1999, 12, 31)
        assert ofx.format_date(date) == "19991231"
        
    def test_format_date_invalid(self):
        date = "Hello!"
        with pytest.raises(AttributeError):
            ofx.format_date(date)
