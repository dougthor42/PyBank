# -*- coding: utf-8 -*-
"""
Handles the OFX tasks such as downloading.

Created on Tue May 12 13:30:13 2015

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
import os.path as osp
import uuid
import http.client
import urllib.parse
import time
import getpass
import logging
from os import urandom

# Third-Party
from docopt import docopt
import requests

# Package / Application
try:
    # Imports used by unit test runners
    from .parseofx import ParseOFX
#    from . import __init__ as __pybank_init
    from . import __version__
    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
        from parseofx import ParseOFX
#        import __init__ as __pybank_init
        from __init__ import __version__
        logging.debug("Imports for Spyder IDE")
    except ImportError:
         # Imports used by cx_freeze
        from parseofx import ParseOFX
        from pybank import __version__
        logging.debug("Imports for Executable")


# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------
# This is black magic - I've no idea where it comes from.
DEFAULT_APP_ID = 'QWIN'
DEFAULT_APP_VERSION = '2200'
DEFAULT_OFX_VERSION = '102'
LINE_ENDING = "\r\n"


# TODO: AMEX: authentication failed: Your request could not be processed
#       because you supplied an invalid identification code or your
#       password was incorrect

# TODO: ChaseCC: authentication failed: USER NOT AUTHORIZED TO ACCESS THE
#       SYSTEM WITH THIS APPLICATION


CHECKING = """
OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:{fileid}

<OFX>
    <SIGNONMSGSRQV1>
        <SONRQ>
            <DTCLIENT>{dtclient}
            <USERID>{uname}
            <USERPASS>{pw}
            <LANGUAGE>ENG
            <FI>
                <ORG>WF
                <FID>3000
            </FI>
            <APPID>QWIN
            <APPVER>2200
        </SONRQ>
    </SIGNONMSGSRQV1>
    <BANKMSGSRQV1>
        <STMTTRNRQ>
            <TRNUID>{trnuid}
            <CLTCOOKIE>4
            <STMTRQ>
                <BANKACCTFROM>
                    <BANKID>{routing}
                    <ACCTID>{acct_num}
                    <ACCTTYPE>CHECKING
                </BANKACCTFROM>
                <INCTRAN>
                    <DTSTART>20150413
                    <INCLUDE>Y
                </INCTRAN>
            </STMTRQ>
        </STMTTRNRQ>
    </BANKMSGSRQV1>
</OFX>
"""

CREDITCARD = """
OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:{fileid}

<OFX>
    <SIGNONMSGSRQV1>
        <SONRQ>
            <DTCLIENT>{dtclient}
            <USERID>{uname}
            <USERPASS>{pw}
            <LANGUAGE>ENG
            <FI>
                <ORG>WF
                <FID>3000
            </FI>
            <APPID>QWIN
            <APPVER>2200
        </SONRQ>
    </SIGNONMSGSRQV1>
    <CREDITCARDMSGSRQV1>
        <CCSTMTTRNRQ>
            <TRNUID>{trnuid}
            <CLTCOOKIE>4
            <CCSTMTRQ>
                <CCACCTFROM>
                    <ACCTID>{cc_num}
                </CCACCTFROM>
                <INCTRAN>
                    <DTSTART>20150413
                    <INCLUDE>Y
                </INCTRAN>
            </CCSTMTRQ>
        </CCSTMTTRNRQ>
    </CREDITCARDMSGSRQV1>
</OFX>
"""

LIST_ACCTS_STR = """
OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:{fileid}

<OFX>
    <SIGNONMSGSRQV1>
        <SONRQ>
            <DTCLIENT>{dtclient}
            <USERID>{uname}
            <USERPASS>{pw}
            <LANGUAGE>ENG
            <FI>
                <ORG>WF
                <FID>3000
            </FI>
            <APPID>QWIN
            <APPVER>2200
        </SONRQ>
    </SIGNONMSGSRQV1>
    <SIGNUPMSGSRQV1>
        <ACCTINFOTRNRQ>
            <TRNUID>{trnuid}
            <CLTCOOKIE>4
            <ACCTINFORQ>
                <DTACCTUP>19700101000000
            </ACCTINFORQ>
        </ACCTINFOTRNRQ>
    </SIGNUPMSGSRQV1>
</OFX>
"""


# ---------------------------------------------------------------------------
### Module Functions
# ---------------------------------------------------------------------------

def docstring():
    """
Summary:
--------
This module handles authentication and connection to the OFX servers as well
as parsing the downloaded OFX data.

Details:
--------
See: https://crackstation.net/hashing-security.htm


Since ofxclient seems like it's not being ported to Python3 *and* because
it's not quite how I'd want user to authenticate, I think that I will have
to roll my own version. Using the source code will help:
https://github.com/captin411/ofxclient/blob/master/ofxclient/client.py


Let's see here...
Usernames will be stored in the database.
Passwords will be stored using keyring, which saves them in the host OS's
password manager.
I think this means that I don't have to salt and hash passwords...


Expected Contents:
------------------
download_data :
    downloads transaction data

"""
    pass


def prompt_password():
    """
    Prompts the user for the password
    """
    return getpass.getpass()


def prompt_user():
    """
    Prompts the user for his username.
    """
    # TODO: Add error handling
    return input("Username: ")


def download_transactions():
    """
    Actually downlaods the transactions
    """
    a = Client()
    b = a.post(CHECKING.format(dtclient=now(),
                               uname=prompt_user(),
                               pw=prompt_password(),
                               fileid=ofx_uid(),
                               trnuid=ofx_uid(),
                               routing="000000000",
                               acct_num="0000000000",
                               )
               )
    for _l in str(b, encoding='utf-8').split("\r\n"):
        logging.debug(_l)
    return b


def create_account():
    """
    Creates an account.

    Accounts consist of an institution and account number. This function
    should add to the SQLite `acct` table.
    """
    pass


def list_accounts():
    """
    Lists accouts at the institution
    """
    pass


def choose_institution():
    """
    Choose an institution.
    """
    pass


def download_accounts():
    """
    Download the accounts at a given institution
    """
    query = LIST_ACCTS_STR.format(dtclient=now(),
                                  uname=prompt_user(),
                                  pw=prompt_password(),
                                  fileid=ofx_uid(),
                                  trnuid=ofx_uid(),
                                  )

    import requests

    headers = {"Content-type": "application/x-ofx",
               "Accept": "*/*, application/x-ofx",
               }

    a = requests.post("https://ofxdc.wellsfargo.com/ofx/process.ofx",
                  query,
                  headers=headers)

    print(a)
    print(a.text)


def main():
    """
    Runs when module is called directly.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    RuntimeError
    """
    docopt(__doc__, version=__version__)

    a = Client()
    b = a.post(LIST_ACCTS_STR.format(dtclient=now(),
                                     uname=prompt_user(),
                                     pw=prompt_password(),
                                     fileid=ofx_uid(),
                                     trnuid=ofx_uid(),
                                     )
               )
    print(b)
    for _l in str(b, encoding='utf-8').split("\r\n"):
        print(_l)
    print("======================================")
    d = download_transactions()
    with open("temp.ofx", 'wb') as openf:
        openf.write(d)
    with open("temp.ofx", 'r') as openf:
        o = ParseOFX(openf)
    print(o.accounts)
    print(o.statement)


#from ofxtools import OFXClient
#import ofxtools
#from ofxtools import OFXTree

if __name__ == "__main__":
#    main()
#    list_accounts()
#    pass
