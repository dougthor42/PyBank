# -*- coding: utf-8 -*-
"""
Handles the OFX tasks such as downloading.

Created on Tue May 12 13:30:13 2015

Usage:
    oxf.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

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
# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
import os
import os.path as osp
import uuid
import time
import getpass
import logging
import json

# Third-Party
from docopt import docopt
import requests

# Package / Application
from .parseofx import ParseOFX
from pybank import __version__


# ---------------------------------------------------------------------------
### Constants
# ---------------------------------------------------------------------------
# This is black magic - I've no idea where it comes from.
DEFAULT_APP_ID = 'QWIN'
DEFAULT_APP_VERSION = '2200'
DEFAULT_OFX_VERSION = '102'
LINE_ENDING = "\r\n"
OFX_HEADERS = {"Content-type": "application/x-ofx",
               "Accept": "*/*, application/x-ofx",
               }

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
### Functions
# ---------------------------------------------------------------------------
def ofx_uid():
    return str(uuid.uuid4().hex)


def now():
    return time.strftime("%Y%m%d%H%M%S", time.localtime())


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


def download_transactions(url, user, pw, routing, acct_num):
    """
    Actually downlaods the transactions
    """
    query = CHECKING.format(dtclient=now(),
                            uname=user,
                            pw=pw,
                            fileid=ofx_uid(),
                            trnuid=ofx_uid(),
                            routing=routing,
                            acct_num=acct_num,
                            )

    b = requests.post(url, query, headers=OFX_HEADERS)

    print(b)
    print(b.text)

    return b.text


def download_accounts(url, user, pw):
    """
    Download the accounts at a given institution
    """
    query = LIST_ACCTS_STR.format(dtclient=now(),
                                  uname=user,
                                  pw=pw,
                                  fileid=ofx_uid(),
                                  trnuid=ofx_uid(),
                                  )

    a = requests.post(url, query, headers=OFX_HEADERS)

    print(a)
    print(a.text)

    return a.text


def get_secrets():
    """
    """
    cwd = os.getcwd()
    fn = "secret.json"
    if "PyBank\\pybank" in cwd:
        fp = osp.join(cwd, fn)
    elif "PyBank" in cwd:
        fp = osp.join(cwd, "pybank", fn)
    else:
        fp = osp.join(r"C:\WinPython34_x64\projects\github\PyBank\pybank", fn)

    with open(fp, 'r') as openf:
        data = json.load(openf)
    return data


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

    secrets = get_secrets()
    bank = "a"

    user = prompt_user()
    pw = prompt_password()

    url = secrets[bank]['url']
    acct_num = secrets[bank]['acct_num']
    routing = secrets[bank]['routing']

    download_accounts(url, user, pw)

    download_transactions(url, user, pw, routing, acct_num)


if __name__ == "__main__":
    main()
