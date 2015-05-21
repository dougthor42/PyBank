# -*- coding: utf-8 -*-
"""
Handles the OFX tasks including downloading and parsing.

Created on Tue May 12 13:30:13 2015

Usage:
    oxf.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""
### #------------------------------------------------------------------------
### Imports
### #------------------------------------------------------------------------
# Standard Library
import sys
import os.path as osp
import hashlib
import uuid
import codecs
import http.client
import urllib.parse
import time
import getpass
import keyring
from os import urandom

# Third-Party
from docopt import docopt

# Package / Application
if __name__ == "__main__":
    sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
from __init__ import VERSION
from pybank.parseofx import ParseOFX


### #------------------------------------------------------------------------
### Module Constants
### #------------------------------------------------------------------------
# This is black magic - I've no idea where it comes from.
DEFAULT_APP_ID = 'QWIN'
DEFAULT_APP_VERSION = '2200'
DEFAULT_OFX_VERSION = '102'
LINE_ENDING = "\r\n"


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

ACCOUNTS = """
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


### #------------------------------------------------------------------------
### Module Functions
### #------------------------------------------------------------------------

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
store_password :
    generates a salt and hashes the password. Sends to sqlite for saving
validate_password :
    validates a given password. Access the sqlite database to retrieve the
    salt.
download_data :
    downloads transaction data

"""
    pass


def salt_and_hash(secret):
    """
    Salts and Hashes a string.

    Parameters:
    -----------
    secret : string
        The secret (username, password, whathaveyou) that you'd like to salt
        and hash.

    Returns:
    --------
    salt : string
        The salt. Yum!

    hashbrowns : string
        The salted hash(brown)ed secret. Delicious.
    """
    salt = codecs.encode(urandom(128), 'hex')
    hashbrowns = hashlib.sha512(salt + secret.encode('utf-8')).hexdigest()
    return salt, hashbrowns


def store_password():
    """
    Store a password.

    1.  Generate Salt using os.urandom()
    2.  Prepend salt to password. Salt can be generated from uuid.uuid4().hex
    3.  Hash the salt+password with SHA256. Alternatively use passlib? But
        then it seems like I can't store the salt.
    4.  Save salt, has to database
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


# XXX:  I won't actually be validating any passwords, will I?
#       Unless I have a master password of sorts. Or somehow have a reversable
#       salt and hash.
def validate_password(secret, salt, hashed):
    """
    Validates a password.

    1.  Retrieve salt and hash
    2.  prepend salt to given password
    3.  Hash salt+password with SHA256
    4.  compare hash to #3

    This function should be limited to 3 executions per second or something.

    This function is actually part of the ofx module.

    Parameters:
    -----------
    secret : string
        The item to validate
    salt : string
        The salt taken from the SQLite database
    hashed : string
        The hash to validate against

    Returns:
    --------
    valid : boolean
        Returns True if the password is valid, false otherwise.
    """
    hashbrowns = hashlib.sha512(salt + secret.encode('utf-8')).hexdigest()
    return hashbrowns == hashed


def download_transactions():
    """
    Actually downlaods the transactions
    """
    a = Client()
    b = a.post(CHECKING.format(uname=prompt_user(), pw=prompt_password()))
    for _l in str(b, encoding='utf-8').split("\r\n"):
        print(_l)
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
    print("Listing accounts")
    a = Client()

    b = a.post(ACCOUNTS.format(dtclient=now(),
                               uname=prompt_user(),
                               pw=prompt_password(),
                               fileid=ofx_uid(),
                               trnuid=ofx_uid()
                               )
               )

    c = str(b, encoding='utf-8')
    for _line in c.split("\r\n"):
        print(_line)
    # TODO: trick OFXParse into thinking we have a file
    # for now, just save a file and then read it.
#    import io
#    with io.StringIO(str(b, encoding='utf-8'), newline='\r\n') as openf:
#        o = ofxparse.OfxParser.parse(openf)

#    with open("temp.ofx", 'wb') as openf:
#        openf.write(b)
#    with open("temp.ofx", 'rb') as openf:
#        o = ofxparse.OfxParser.parse(openf)
#    print(o.account)
#    print(o.account.number)

    d = ParseOFX(c)
    d.parse_accounts()
    print(d.descr)


    return b


def choose_institution():
    """
    Choose an institution.
    """
    pass

def download_accounts():
    """
    Download the accounts at a given institution
    """
    pass

def save_account():
    """
    Save account info to the database.
    """
    pass

def save_institution():
    """
    Save institution info to the database.
    """
    pass

def read_institution():
    """
    Read insitution info from the database.
    """
    pass

def read_account():
    """
    Read account info from the database.
    """
    pass



### #------------------------------------------------------------------------
### Re-implementing ofxclient
### #------------------------------------------------------------------------
#
#   Original code Copyright (c) 2012 David Bartle
#
#   https://github.com/captin411/ofxclient
#
#   Slightly modified by D. Thor, May 2015
#
#   Modifications include but not limited to:
#
#   + Updated for Python 3.3+
#   + Additional docstrings and comments
#
### #------------------------------------------------------------------------


def ofx_uid():
    return str(uuid.uuid4().hex)


class Client(object):
    """
    """
    def __init__(self,
                 institution=None,
                 inst_id=ofx_uid(),
                 app_id=DEFAULT_APP_ID,
                 app_version=DEFAULT_APP_VERSION,
                 ofx_version=DEFAULT_OFX_VERSION,
                 ):
        self.institution = institution
        self.inst_id = inst_id
        self.app_id = app_id
        self.app_version = app_version
        self.ofx_version = ofx_version
        self.cookie = 3

    def authenticated_query(self,
                            with_message=None,
                            username=None,
                            password=None,
                            ):
        """
        Run an authenticated query.

        Parameters:
        -----------
        with_message : string, optional
            Additional message to append to the contents.

        username : string, optional
            Username to authenticate with. If ``None``, defaults to the
            username stored in self.institution

        password : string, optional
            Password to authenticate with. If ``None``, defaults to the
            password stored in self.institution

        Returns:
        --------
        The results from the query.

        """
        u = username or self.institution.username
        p = password or self.institution.password

        contents = ['OFX', self._signOn(username=u, password=p)]
        if with_message:
            contents.append(with_message)
        return str.join(LINE_ENDING, [self.header(), _tag(*contents)])

    def bank_account_query(self, number, date, account_type, bank_id):
        """
        Query the checking or savings account statements.

        Parameters:
        -----------
        number : string
            the account number
        date : string
            The date start string. Will pull transactsion from this date
            onward. Formatted as ``YYYYMMDDHHMMSS``
        account_type : string
            The account type to query.
        bank_id :
            The bank id.

        Returns:
        --------
        OFX-formatted string of transactions for the given account.

        """
        return self.authenticated_query(self._bareq(number,
                                                    date,
                                                    account_type,
                                                    bank_id),
                                        )

    def account_list_query(self, date='19700101000000'):
        """
        Query the account list

        Parameters:
        -----------
        date : string
            The date to query accounts from. Date format is
            ``YYYYMMDDHHMMSS``, so ``2015-03-02 12:57:36` would be formatted
            as ``20150302125736``.

            I *think* that any accounts created before this date will
            not be returned.

        Returns:
        --------
        OFX-formatted string of accounts at a given institution.

        """
        return self.authenticated_query(self._acctreq(date))

    def post(self, query):
        """
        Execute (POST) the query to the website.
        """
        o = urllib.parse.urlparse("https://ofxdc.wellsfargo.com/ofx/process.ofx")
        host = o.netloc
        selector = o.path
        conn = http.client.HTTPSConnection(host)
        conn.request("POST", selector, query,
                  {"Content-type": "application/x-ofx",
                   "Accept": "*/*, application/x-ofx"},
                   )
        res = conn.getresponse()
        response = res.read()
        res.close()
        return response

    def next_cookie(self):
        """
        Increment the cookie number.
        """
        self.cookie += 1
        return str(self.cookie)

    def header(self):
        parts = ["OFXHEADER:100",
                 "DATA:OFXSGML",
                 "VERSION:{}".format(int(self.ofx_version)),
                "SECURITY:NONE",
                "ENCODING:USASCII",
                "CHARSET:1252",
                "COMPRESSION:NONE",
                "OLDFILEUID:NONE",
                "NEWFILEUID:{}".format(ofx_uid()),
                "",
                ]
        return str.join(LINE_ENDING, parts)

    def _signOn(self, username=None, password=None):
        """
        Generate signon message
        """
        u = username or self.institution.username
        p = password or self.institution.password
        fidata = [_field("ORG", self.institution.org)]
        if self.institution.id:
            fidata.append(_field("FID", self.institution.id))

        client_uid = ''
        if str(self.ofx_version) == '103':
            client_uid = _field('CLIENTUID', self.id)

        return _tag("SIGNONMSGSRQV1",
                    _tag("SONRQ",
                         _field("DTCLIENT", now()),
                         _field("USERID", u),
                         _field("USERPASS", p),
                         _field("LANGUAGE", "ENG"),
                         _tag("FI", *fidata),
                         _field("APPID", self.app_id),
                         _field("APPVER", self.app_version),
                         client_uid
                         ))

    def _acctreq(self, dtstart):
        """
        Accounts Request

        Gets a list of accounts as an OFX-formatted string.
        """
        req = _tag("ACCTINFORQ", _field("DTACCTUP", dtstart))
        return self._message("SIGNUP", "ACCTINFO", req)

    # this is from _ccreq below and reading page 176 of the latest OFX doc.
    def _bareq(self, acctid, dtstart, accttype, bankid):
        """
        Bank Account Request

        Returns the bank statement as an OFX-formatted string
        """
        req = _tag("STMTRQ",
                   _tag("BANKACCTFROM",
                        _field("BANKID", bankid),
                        _field("ACCTID", acctid),
                        _field("ACCTTYPE", accttype)),
                   _tag("INCTRAN",
                        _field("DTSTART", dtstart),
                        _field("INCLUDE", "Y")))
        return self._message("BANK", "STMT", req)

    def _ccreq(self, acctid, dtstart):
        """
        Credit Card Request

        Returns the credit card statement as an OFX-formatted string.
        """
        req = _tag("CCSTMTRQ",
                   _tag("CCACCTFROM", _field("ACCTID", acctid)),
                   _tag("INCTRAN",
                        _field("DTSTART", dtstart),
                        _field("INCLUDE", "Y")))
        return self._message("CREDITCARD", "CCSTMT", req)

    def _invstreq(self, brokerid, acctid, dtstart):
        """
        Investment Request

        Returns investment account statement as an OFX-formatted string.
        """
        req = _tag("INVSTMTRQ",
                   _tag("INVACCTFROM",
                        _field("BROKERID", brokerid),
                        _field("ACCTID", acctid)),
                   _tag("INCTRAN",
                        _field("DTSTART", dtstart),
                        _field("INCLUDE", "Y")),
                   _field("INCOO", "Y"),
                   _tag("INCPOS",
                        _field("DTASOF", now()),
                        _field("INCLUDE", "Y")),
                   _field("INCBAL", "Y"))
        return self._message("INVSTMT", "INVSTMT", req)

    def _message(self, msgType, trnType, request):
        return _tag(msgType+"MSGSRQV1",
                    _tag(trnType+"TRNRQ",
                         _field("TRNUID", ofx_uid()),
                         _field("CLTCOOKIE", self.next_cookie()),
                         request))


def _field(tag, value):
    return "<"+tag+">"+value


def _tag(tag, *contents):
    return str.join(LINE_ENDING, ["<"+tag+">"]+list(contents)+["</"+tag+">"])


def now():
    return time.strftime("%Y%m%d%H%M%S", time.localtime())


### #------------------------------------------------------------------------
### End Re-implementing ofxclient
### #------------------------------------------------------------------------


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
    docopt(__doc__, version=VERSION)
#    raise RuntimeError("This module is not meant to be run by itself")
    salt, hashed = salt_and_hash("Secret")
    print(validate_password("Secret", salt, hashed))
    print()
    a = Client()
    b = a.post(ACCOUNTS.format(uname=prompt_user(), pw=prompt_password()))
    print(b)
    for _l in str(b, encoding='utf-8').split("\r\n"):
        print(_l)
    print("======================================")
    d = download_transactions()
    with open("temp.ofx", 'wb') as openf:
        openf.write(d)
    with open("temp.ofx", 'rb') as openf:
        o = ofxparse.OfxParser.parse(openf)
    print(o.account.number)
    print(o.account.routing_number)
    print(o.account.statement)
    print(o.account.statement.start_date)
    print(o.account.statement.end_date)
    print(o.account.statement.transactions)
    print(o.account.statement.balance)
    print(o.account.statement.available_balance)


if __name__ == "__main__":
#    main()
    list_accounts()
