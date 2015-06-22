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
import sys
import unittest
import unittest.mock as mock
import os.path as osp
import io
import datetime

# Third-Party
from docopt import docopt
from bs4 import BeautifulSoup

# Package / Application
try:
    from .. import parseofx
except (SystemError, ImportError):
    if __name__ == "__main__":
        # Allow module to be run as script
        print("Running module as script")
        sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
        import parseofx
    else:
        raise


"""
TODO List:
----------

[ ] Raise error on unknown or not yet implemented tag
[ ] Header parse OK
[ ] Accounts parse OK

"""

### #------------------------------------------------------------------------
### Constants
### #------------------------------------------------------------------------
EXAMPLE_OFX_ACCOUNT_LIST = b"""
OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:newfileuid

<OFX>
    <SIGNONMSGSRSV1>
        <SONRS>
            <STATUS>
                <CODE>0
                <SEVERITY>INFO
            </STATUS>
            <DTSERVER>20150520232950.608[0:GMT]
            <LANGUAGE>ENG
            <FI>
                <ORG>FI_ORGNAME
                <FID>123456
            </FI>
        </SONRS>
    </SIGNONMSGSRSV1>
    <SIGNUPMSGSRSV1>
        <ACCTINFOTRNRS>
            <TRNUID>trnuid
            <STATUS>
                <CODE>0
                <SEVERITY>INFO
            </STATUS>
            <CLTCOOKIE>4
            <ACCTINFORS>
                <DTACCTUP>20150520232957.222[0:GMT]
                <ACCTINFO>
                    <DESC>Checking
                    <BANKACCTINFO>
                        <BANKACCTFROM>
                            <BANKID>bankid_bank_account_num
                            <ACCTID>acctid_routing_num
                            <ACCTTYPE>CHECKING
                        </BANKACCTFROM>
                        <SUPTXDL>Y
                        <XFERSRC>Y
                        <XFERDEST>Y
                        <SVCSTATUS>ACTIVE
                    </BANKACCTINFO>
                    <BPACCTINFO>
                        <BANKACCTFROM>
                            <BANKID>bankid_bank_account_num
                            <ACCTID>acctid_routing_num
                            <ACCTTYPE>CHECKING
                        </BANKACCTFROM>
                        <SVCSTATUS>ACTIVE
                    </BPACCTINFO>
                </ACCTINFO>
                <ACCTINFO>
                    <DESC>Visa
                    <CCACCTINFO>
                        <CCACCTFROM>
                            <ACCTID>credit_card_num
                        </CCACCTFROM>
                        <SUPTXDL>Y
                        <XFERSRC>Y
                        <XFERDEST>Y
                        <SVCSTATUS>ACTIVE
                    </CCACCTINFO>
                </ACCTINFO>
            </ACCTINFORS>
        </ACCTINFOTRNRS>
    </SIGNUPMSGSRSV1>
</OFX>
"""

### #------------------------------------------------------------------------
### UnitTests
### #------------------------------------------------------------------------


# XXX: Use subtest context manager! See:
# https://docs.python.org/3/library/unittest.html#distinguishing-test-iterations-using-subtests

class TestCloseTags(unittest.TestCase):
    """
    Tests the parseofx.close_tags function.
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_close_tags_ok(self):
        """ Check tags get closed """
        open_tags = io.StringIO("""
            <STATUS>
                <CODE>0
                <SEVERITY>INFO
            </STATUS>
                """)
        actual = "<STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS>"
        result = parseofx.close_tags(open_tags).read()
        self.assertEqual(result, actual)

    # TODO: Look into what's going on here
    @unittest.skip("Need to fix.")
    def test_close_tags_ok2(self):
        """ Check that tags get closed also """
        open_tags = io.StringIO("""
                <CODE>0
                <SEVERITY>INFO
                """)
        actual = "<CODE>0</CODE><SEVERITY>INFO</SEVERITY>"
        result = parseofx.close_tags(open_tags).read()
        self.assertEqual(result, actual)


@unittest.skip("Not implemented")
class TestStripHeader(unittest.TestCase):
    """ Tests the strip_header function """
    pass


@unittest.skip("Not implemented")
class TestParseOFX(unittest.TestCase):
    """ Tests the ParseOFX class """
    pass


class TestParseStatus_OKAllTags(unittest.TestCase):
    """ Check the parse_status function """
    def setUp(self):
        self.soup = BeautifulSoup("""
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
                <MESSAGE>Hello</MESSAGE>
            </STATUS>
            """, 'xml')
        # TODO: DO I want to have result be an attribute? or recalc each time?
        self.result = parseofx.parse_status(self.soup)

    def tearDown(self):
        pass

    def test_attributes_exist(self):
        """
        Checks that all of the Status attributes exist

        Does not verify values.
        """
        attributes = ['code', 'severity', 'message']
        for attr in attributes:
            with self.subTest(attr=attr):
                fail_msg = "ParseOFX.Status doesn't have `{}`".format(attr)
                self.assertTrue(hasattr(self.result, attr), fail_msg)

    def test_code_value_correct(self):
        """
        Check that the value of `code` is correct
        """
        fail_msg = "Status.code parsed incorrectly!"
        self.assertEqual(self.result.code, 0, fail_msg)

    def test_severity_value_correct(self):
        """
        Check that the value of `severity` is correct
        """
        fail_msg = "Status.severity parsed incorrectly!"
        self.assertEqual(self.result.severity, "INFO", fail_msg)

    def test_message_value_correct(self):
        """
        Check that the value of `message` is correct.
        """
        fail_msg = "Status.message parsed incorrectly!"
        self.assertEqual(self.result.message, "Hello", fail_msg)


class TestParseStatus_OKNoMessage(unittest.TestCase):
    """
    Tests that parse_status works when there is no message tag.
    """
    def setUp(self):
        self.soup = BeautifulSoup("""
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
            """, 'xml')
        self.result = parseofx.parse_status(self.soup)

    def tearDown(self):
        pass

    def test_message_is_none(self):
        """ Check that no message is found """
        self.assertIsNone(self.result.message)


# TODO: See if I want to move this to a single class
class TestParseStatus_FailOnInvalidXML(unittest.TestCase):
    """
    Tests that parse_status fails on invalid XML.
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_raise_on_missing_code(self):
        """ Check that AttributeError raised if `code` is missing """
        soup = BeautifulSoup("""
            <STATUS>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
            """, 'xml')
        with self.assertRaises(AttributeError):
            parseofx.parse_status(soup)

    def test_raise_on_missing_severity(self):
        """ Check that AttributeError raised if `severity` is missing """
        soup = BeautifulSoup("""
            <STATUS>
                <CODE>0</CODE>
            </STATUS>
            """, 'xml')
        with self.assertRaises(AttributeError):
            parseofx.parse_status(soup)



class TestParseDatetime(unittest.TestCase):
    """
    Tests the parse_datetime function.
    """
    def test_parse_datetime_fail_missing_tag(self):
        """
        Check parse_datetime fails if there is no datetime tag in the soup.
        """
        soup = BeautifulSoup("""
            <SONRS>
                <STATUS>
                    <CODE>0
                    <SEVERITY>INFO
                </STATUS>

                <LANGUAGE>ENG
                <FI>
                    <ORG>FI_ORGNAME
                    <FID>123456
                </FI>
            </SONRS>""", 'xml')
        with self.assertRaises(AttributeError):
            parseofx.parse_datetime(soup)

    def test_parse_datetime_OK(self):
        """ Check parse_datetime is OK """
        soup = BeautifulSoup("""<SONRS>
            <STATUS>
                <CODE>0
                <SEVERITY>INFO
            </STATUS>
            <DTSERVER>20150520232950.608[0:GMT]
            <LANGUAGE>ENG
            <FI>
                <ORG>FI_ORGNAME
                <FID>123456
            </FI>
        </SONRS>""", 'xml')

        result = parseofx.parse_datetime(soup)
        self.assertIsInstance(result, datetime.datetime)


class TestConvertDatetime(unittest.TestCase):
    """
    Tests the convert_datetime function.
    """
    # TODO: Add more known values
    known_values = [("20150302164711.123",
                     datetime.datetime(2015, 3, 2, 16, 47, 11, 123000)),
                    ("19980101010101.123[-8:PDT]",
                     datetime.datetime(1998, 1, 1, 9, 1, 1, 123000)),

                    ]

    malformed_fmts = [
                      "20001703",               # invalid month
                      "20150147",               # invalid day
#                      "20151203262626",         # invalid hour
#                      "20151203206226",         # invalid minute
#                      "20151203201361",         # invalid second
#                      "199807211237",           # missing seconds
                      "2015",                   # missing month, day
                      ]

    def test_known_values(self):
        """ Check known values for convert_datetime """
        for dt_str, expected in self.known_values:
            with self.subTest(_dt_str=dt_str, _expected=expected):
                result = parseofx.convert_datetime(dt_str)
                self.assertEqual(expected, result)

    def test_bad_formats(self):
        """ Check that malformed datetime strings raise errors """
        for dt_str in self.malformed_fmts:
            with self.subTest(malformed_str=dt_str):
                with self.assertRaises(ValueError):
                    parseofx.convert_datetime(dt_str)


def main():
    """
    Main entry point
    """
    docopt(__doc__, version="0.0.1")    # TODO: pull VERSION from __init__
    unittest.main(verbosity=1)


if __name__ == "__main__":
    main()
