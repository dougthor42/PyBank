# -*- coding: utf-8 -*-
"""
Reimplemtation of Jerry Seutter's ofxparse.
https://github.com/jseutter/ofxparse

Created on Wed May 20 16:36:40 2015

@author: dthor

Usage:
    ofxparse.py FILE

Options:
    -h --help           # Show this screen.
    --version           # Show version.

Notes:
------
See http://www.ofx.net/DeveloperSolutions.aspx

Goal: read though the file / string only once.
"""

### #------------------------------------------------------------------------
### Imports
### #------------------------------------------------------------------------
# Standard Library
import sys
import os.path as osp
from enum import Enum

# Third-Party
from docopt import docopt

# Package / Application
if __name__ == "__main__":
    sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
from __init__ import VERSION


### #------------------------------------------------------------------------
### Module Constants
### #------------------------------------------------------------------------
# Some of this is black magic - I've no idea where it comes from.
DEFAULT_APP_ID = 'QWIN'
DEFAULT_APP_VERSION = '2200'
DEFAULT_OFX_VERSION = '102'
LINE_ENDING = "\r\n"


class ParseOFX(object):
    """
    Main entry point for parsing OFX files and strings.

    Hacked together OFX Parser, because ofxparse seems dead
    """
    def __init__(self, ofx_data):
        # TODO: accept a file, opened file, stream, or string
        #       for now, just accept Python3 text
        self.ofx_data = ofx_data

        self.bankid = []
        self.descr = []

    def parse_accounts(self):
        for line in self.ofx_data.split('\r\n'):
            if line.startswith("<DESC>"):
                self.descr.append(line[6:])
            if line.startswith("<BANKID>"):
                self.bankid.append(line[8:])


class AccountType(Enum):
    """ Account Types """
    Unknown = 0
    Bank = 1
    CreditCard = 2
    Investment = 3


class Account(object):
    """
    An OFX account object.
    """
    def __init__(self):
        self.statement = None
        self.account_id = ''
        self.routing_number = ''
        self.branch_id = ''
        self.account_type = ''
        self.institution = None
        self.type = AccountType.Unknown
        # Used for error tracking
        self.warnings = []


class InvestmentAccount(Account):
    """
    An OFX Investment Account object
    """
    def __init__(self):
        super(InvestmentAccount, self).__init__()
        self.brokerid = ''


class Statement(object):
    """
    An OFX Statement object
    """
    pass


class InvestmentStatement(object):
    """
    An OFX Investment Statement object
    """
    pass


class Transaction(object):
    """
    An OFX Tranaction object
    """
    pass


class InvestmentTransaction(object):
    """
    An OFX Investment Transaction object
    """
    pass


class Institution(object):
    """
    An OFX Institution object.

    Gets filled in by `FI.ORG` and `FI.FID`
    """
    def __init__(self):
        self.organization = None
        self.fid = None



EXAMPLE_OFX_ACCOUNT_LIST = """
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
                    <BANKACCTINFO>      <!-- Bank Account Info -->
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
                    <BPACCTINFO>         <!-- Bank *Payment* Account Info -->
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


def main():
    """ Code to run when module called directly, just some quick checks. """
    docopt(__doc__, version=VERSION)

if __name__ == "__main__":
    main()
