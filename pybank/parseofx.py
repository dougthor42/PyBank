# -*- coding: utf-8 -*-
"""
Reimplemtation of Jerry Seutter's ofxparse.
https://github.com/jseutter/ofxparse

Created on Wed May 20 16:36:40 2015

@author: dthor

Usage:
    parseofx.py
    parseofx.py FILE

Options:
    FILE                # file to parse
    -h --help           # Show this screen.
    --version           # Show version.

Notes:
------
See http://www.ofx.net/DeveloperSolutions.aspx

So, Jerry's ofxparse does the following, if I'm reading it correctly:

1.  Works on a seekable stream such as an open file. I plan on doing the
    same thing, but making it work with Python3 only - none of this `six`
    or `2to3` crap.

2.  Preprocesses the stream by added closing tags to everything that doesn't
    already have it. This makes it look more like standard XML.

    Example::

        <STATUS>                --->>>  <STATUS>
            <CODE>0             --->>>      <CODE>0</CODE>
            <SEVERITY>INFO      --->>>      <SEVERITY>INFO</SEVERITY>
        </STATUS>               --->>>  </STATUS>

3.  Reads the headers, and then essentially gets rid of them by setting the
    start position of the file to be after the header (see the `save_pos`
    generator).

4.  Takes the new, processed stream and parses the now-valid XML with
    BeautifulSoup.

5.  Uses BeautifulSoup.find() to find all the useful tags and adds them to
    the `Ofx` object (who's "__str__" method prints nothing...)


Other Items:
------------
+ Will need Merchant Category Codes (MCC). See
  https://github.com/greggles/mcc-codes for a good source. Would also like
  to auto-update that...

"""

### #------------------------------------------------------------------------
### Imports
### #------------------------------------------------------------------------
# Standard Library
import sys
import io
import re
import datetime
import decimal
import os.path as osp
from enum import Enum

# Third-Party
from docopt import docopt
from bs4 import BeautifulSoup

# Package / Application
if __name__ == "__main__":
    sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
#from __init__ import VERSION


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

    Parameters:
    -----------
    ofx_data : string, string stream (io.StringIO), or opened file stream
        The ofx data to parse.
    newline : string, optional
        The character that denotes a new line in ofx_data.

    Returns:
    --------
    something : something
        Something something something something's something.

    Notes:
    ------
    If ofx_data is a string, a io.StringIO stream is created from it upon
    __init__. All all actions act on this stream.

    ParseOFX does *not* close any streams (# XXX: is this what I want?)

    Attributes:
    ------------------
    stuff

    Methods:
    ---------------
    None

    Private Attributes:
    -------------------
    None

    Private Methods:
    ----------------
    None

    """
    def __init__(self, ofx_data, newline=LINE_ENDING):
        self.newline = newline
        self.insitution = None
        self.accounts = []
        self.bankid = []
        self.descr = []
        self.header = None
        self.soup = None
        self.sonrs = None
        self.sonrq = None
        self.statement = None
        self.fi = None

        # convert ofx_data to a stream
        # TODO: Handle closing of opened streams
        print(type(ofx_data))
        if type(ofx_data) == str:
            ofx_data = io.StringIO(ofx_data, newline=self.newline)
        elif type(ofx_data) == bytes:
            ofx_data = str(ofx_data, encoding='utf-8')
            ofx_data = io.StringIO(ofx_data, newline=self.newline)
        elif type(ofx_data) == io.BufferedReader:
            ofx_data = io.StringIO(ofx_data.read(), newline=self.newline)
#            pass
        elif type(ofx_data) == io.StringIO:
            pass
        elif type(ofx_data) == io.TextIOWrapper:
            ofx_data = io.StringIO(ofx_data.read(), newline=self.newline)
        else:
            error_text = ("Arguement `ofx_data` must be a string, opened",
                          " file stream, or StringIO stream.",
                          )
            raise TypeError(error_text)

        self.ofx_data = ofx_data

        self.insitution = None
        self.accounts = []

        # TODO: decide if I want the file preprocessing to happen here
        #       or within parse().
        #       Advantage of within parse() is that then others can call
        #       parse on unclean files

        # Start the parsing.
        self.parse()

    def parse_accounts(self):
        """ Temporary parser, will delete later """
        self.bankid = []
        self.descr = []

        for line in self.ofx_data.split('\r\n'):
            if line.startswith("<DESC>"):
                self.descr.append(line[6:])
            if line.startswith("<BANKID>"):
                self.bankid.append(line[8:])

    def parse(self):
        """
        Parses the entire file or string
        """
        # Process the file to make it valid XML for BeautifulSoup
        self.ofx_data, self.header = strip_header(self.ofx_data)
        self.ofx_data = close_tags(self.ofx_data)

        # Parse it with BeautifulSoup
        self.soup = BeautifulSoup(self.ofx_data, "xml")

        # raise an error if the file's empty
        if len(self.soup.contents) == 0:
            raise EOFError("The OFX file was empty, I guess?")

        self._find_ofx_items()

        return self.soup

    def _find_ofx_items(self):
        """
        Searches for and saves all of the OFX items
        """
        # TODO: Add request items
        # TODO: Refactor the following code
        #       Looks like I could make one or two generic functions
        #       and then just pass the tag string (and perhaps the method).


        ### Sign On Message Responses #######################################

        # Find the single Sign On Response
        self.sonrs_soup = self.soup.find("SONRS")
        if self.sonrs_soup is not None:
            self._parse_sonrs()

        # Find the single Sign On Request
        self.sonrq_soup = self.soup.find("SONRQ")
        if self.sonrq_soup is not None:
            self._parse_sonrq()

        # Find the Financial Institution
        self.fi_soup = self.soup.find("FI")
        if self.fi_soup is not None:
            self._parse_financial_institution()


        ### Statements ######################################################

        # Find the Account Info Response
        self.acctinfors_soup = self.soup.find("ACCTINFORS")
        if self.acctinfors_soup is not None:
            self._parse_acct_info_response()

        # Find all of the Bank Statement Responses
        # Note: Could use soup("STMTRS"); its the same as soup.findAll()
        self.stmttrnsrs_soup = self.soup.find("STMTTRNRS")
        if (self.stmttrnsrs_soup is not None
            and len(self.stmttrnsrs_soup) != 0):        # I prefer explicit
            self._parse_bank_statement_response()

        # Find all of the Credit Card Statement Responses
        self.ccstmtrs_soup = self.soup.findAll("CCSTMTRS")
        if len(self.ccstmtrs_soup) != 0:
            self._parse_cc_statement_response()

        # Find all of the Investment Statement Responses
        self.invstmtrs_soup = self.soup.findAll("INVSTMTRS")
        if len(self.invstmtrs_soup) != 0:
            self._parse_inv_statement_response()

    def _parse_sonrs(self):
        """
        Parses the Sign On Response (SONRS)
        """
        self.sonrs = SignOnResponse()
        self.sonrs.status = parse_status(self.sonrs_soup)
        self.sonrs.dt_server = parse_datetime(self.sonrs_soup)
        self.sonrs.language = self.soup.find("LANGUAGE").contents[0]
#        self.sonrs.fi = self._parse_financial_institution()

    def _parse_sonrq(self):
        """
        Parses the Sign On Request (SONRQ)
        """
        self.sonrq = SignOnRequest()
        self.sonrq.dt_client = parse_datetime(self.sonrq_soup)
        self.sonrq.user_id = self.soup.find("USERID").contents[0]
        self.sonrq.user_password = self.soup.find("USERPASS").contents[0]
        self.sonrq.language = self.soup.find("LANGUAGE").contents[0]
        self.sonrq.app_id = self.soup.find("APPID").contents[0]
        self.sonrq.app_version = self.soup.find("APPVER").contents[0]

    def _parse_bank_statement_response(self):
        """
        Parses the Statement Response (STMTRS)
        """
        stmt = OFXStatement()
        stmt.dtstart = parse_datetime(self.stmttrnsrs_soup, "DTSTART")
        stmt.dtend = parse_datetime(self.stmttrnsrs_soup, "DTEND")

        # TODO: enum?
        stmt.curdef = self.stmttrnsrs_soup.find("CURDEF").contents[0]

        # TODO: decimal.Decimal
        ledger_bal_soup = self.stmttrnsrs_soup.find("LEDGERBAL")
        stmt.ledger_balance = parse_balance(ledger_bal_soup)
        avail_bal_soup = self.stmttrnsrs_soup.find("AVAILBAL")
        stmt.available_balance = parse_balance(avail_bal_soup)

        # Find every transaction
        trans = OFXTransaction()
        stmt.transactions = []
        for transaction_soup in self.stmttrnsrs_soup.findAll("STMTTRN"):
            #
            trans = parse_transaction(transaction_soup)
            stmt.transactions.append(trans)

        self.statement = stmt


    def _parse_cc_statement_response(self):
        """
        Parses the Credit Card Statement Response (CCSTMTRS)
        """
        pass

    def _parse_inv_statement_response(self):
        """
        Parses the Investment Statement Response (INVSTMTRS)
        """
        pass

    def _parse_acct_info_response(self):
        """
        Parses the Account Info Response (ACCTINFORS)
        """
        dt = parse_datetime(self.acctinfors_soup)

        for _acct_info in self.acctinfors_soup.findAll("ACCTINFO"):
            acct = Account()

            # TODO: optimize
            if _acct_info.find("INVACCTINFO"):
                acct = InvestmentAccount()
                acct.account_type = AccountType.investment
                # TODO: more investment account items
            elif _acct_info.find("CCACCTINFO"):
                acct = CreditCardAccount()
                acct.account_type = AccountType.creditcard
            elif _acct_info.find("BANKACCTINFO"):
                acct = BankAccount()
                acct.account_type = AccountType.bank
                acct.bank_id = _acct_info.find("BANKID").contents[0]
            else:
                raise TypeError("Unknown Account Type")

            # Items in every Account
            acct.desc = _acct_info.find("DESC").contents[0]
            acct.account_id = _acct_info.find("ACCTID").contents[0]
            acct.suptxdl = _acct_info.find("SUPTXDL").contents[0]
            acct.xfersrc = _acct_info.find("XFERSRC").contents[0]
            acct.xferdest = _acct_info.find("XFERDEST").contents[0]
            acct.svcstatus = _acct_info.find("SVCSTATUS").contents[0]

            acct.dt_acct_up = dt

            self.accounts.append(acct)

    def _parse_financial_institution(self):
        """
        Parses the Financial Institution (FI)
        """
        self.fi = FinancialInstitution()
        self.fi.org = self.fi_soup.find('ORG').contents[0]
        self.fi.fid = self.fi_soup.find('FID').contents[0]


def parse_status(soup):
    """
    Slurps up the OFX Status from the soup.

    Parameters:
    -----------
    soup : BeautifulSoup4 XML object
        The XML to parse for status.

    Returns:
    --------
    status : parseofx.Status object
        The OXF status.

    """
    status = Status()
    try:
        status.code = int(soup.find('CODE').contents[0])
        status.severity = soup.find('SEVERITY').contents[0]
    except AttributeError:
        raise AttributeError("Could not find 'CODE' or 'SEVERITY' tag.")
    try:
        status.message = soup.find('MESSAGE').contents[0]
    except AttributeError:
        status.message = None

    return status


def parse_datetime(soup, tag=None):
    """
    Parses the OFX datetime.

    Tries DTACCTUP, DTSTART, DTCLIENT, DTSERVER

    ::

        There is one format for representing dates, times, and time
        zones. The complete form is:

        YYYYMMDDHHMMSS.XXX [gmt offset[:tz name]]
            -- OFX Standard 2.1.1, Section 3.2.8.1

    This will need to handle partial times too.

    For now, just grab the string.

    Parameters:
    -----------
    soup : BeautifulSoup4 XML object
        The XML to parse the datetime from.

    Returns:
    --------
    ofx_dt : datetime.datetime object
        The parsed date.

    """
    if tag is None:
        dt_tags = ["DTACCTUP", "DTCLIENT", "DTSERVER", "DTSTART", "DTEND",
                   "DTPOSTED", "DTASOF"]
    else:
        dt_tags = [tag]
    for tag in dt_tags:
        try:
            # TODO: SONRS can have more than one DT!
            ofx_dt = convert_datetime(soup.find(tag).contents[0])
            return ofx_dt
        except AttributeError:
            continue
    else:
        raise AttributeError("Datetime tag not found")


def convert_datetime(ofx_dt):
    """
    Converts an OXF datetime string to a Python datetime object.

    Raises error if the string is ont a recognized format (such as missing
    seconds). Raises error if the conversion to datetime fails.
        XXX: But if I've verified the string with regex, why would it fail?

    Parameters:
    -----------
    ofx_dt : string
        An OFX datetime-formatted string.

    Returns:
    --------
    timestamp : datetime.datetime object
        The unaware (naive) timestamp in GMT time.

    Notes:
    ------
    See OFX Standard 2.1.1, section 3.2.8 for more information.

    """
    # Get the time zone
    tz_type = re.search("\[(?P<tz>[-+]?\d+\.?\d*)\:\w*\]$", ofx_dt)
    if tz_type is not None:
        tz = float(tz_type.group('tz'))
    else:
        tz = 0

    tz_offset = datetime.timedelta(hours=tz)

    strptime = datetime.datetime.strptime

    # Parse the string, falling back on various formats
    # TODO: Change logic to use regex instead.
    #       1st, match string to re. if no match, then raise ValueError
    #       2nd, parse string to datetime object. If fail, raise.
    try:
        fmt = "%Y%m%d%H%M%S.%f[%z:%Z]"
        local_dt = strptime(ofx_dt, fmt)
    except ValueError:
        try:
            fmt = "%Y%m%d%H%M%S.%f"
            local_dt = strptime(ofx_dt[:18], fmt)
        except ValueError:
            try:
                fmt = "%Y%m%d%H%M%S"
                local_dt = strptime(ofx_dt[:14], fmt)
            except ValueError:
                try:
                    fmt = "%Y%m%d"
                    local_dt = strptime(ofx_dt[:8], fmt)
                except ValueError:
                    raise ValueError("Unknown OFX datetime format")

    timestamp = local_dt - tz_offset
    return timestamp


def parse_transaction(soup):
    """
    Parses an OFX Transaction

    Parameters:
    -----------
    soup : bs4.BeautifulSoup object
        The XML to parse

    Returns:
    --------
    transaction : OFXTransaction object
        The parsed transaction object.

    """
    transaction = OFXTransaction()
    transaction = BankTransaction()

    transaction.trntype = soup.find("TRNTYPE").contents[0]     # TODO: Enum?
    transaction.dtposted = parse_datetime(soup, "DTPOSTED")
    try:
        transaction.dtuser = parse_datetime(soup, "DTUSER")
    except AttributeError:
        transaction.dtuser = None
    transaction.trnamt = soup.find("TRNAMT").contents[0]    # TODO: Decimal
    transaction.fitid = soup.find("FITID").contents[0]      # TODO: int?
    try:
        transaction.checknum = soup.find("CHECKNUM").contents[0]    # TODO: int?
    except AttributeError:
        transaction.checknum = None

    transaction.name = soup.find("NAME").contents[0]
    try:
        transaction.memo = soup.find("MEMO").contents[0]
    except AttributeError:
        transaction.memo = None

    return transaction


def parse_balance(soup):
    """
    Parses an OFX Balance object from the soup.

    Parameters:
    -----------
    soup : bs4.BeautifulSoup object
        The XML to parse.

    Returns:
    --------
    balance : OFXBalance object
        The parsed balance object.
    """
    balance = OFXBalance()
    balance.balance = decimal.Decimal(soup.find("BALAMT").contents[0])
    balance.as_of_date = parse_datetime(soup, "DTASOF")
    return balance

def strip_header(ofx_stream):
    """
    Strips and saves the header from the OFX data.

    Parameters:
    -----------
    ofx_stream : io.IOBase object
        The opened file object stream or StringIO stream of OFX data

    Returns:
    --------
    ofx_stream : io.IOBase object
        An opened file object or StringIO stream of OFX data with the
        header removed.

    header : dict
        A dictionary containing the header.

    """
    header = {}

    # Read subset of the file in case it's huge; find where the header ends
    header_str = ofx_stream.read(2048)
    header_end = header_str.find('<')
    header_str = header_str[:header_end]

    # iterate though the header, saving key-value pairs and skipping blanks
    for line in header_str.splitlines():
        if line.strip() == "":
            continue

        key, value = line.split(":")
        key, value = key.strip().upper(), value.strip().upper()
        if value == 'NONE':
            value = None

        header[key] = value

    # Seek back to the end of the header and overwrite the original stream.
    ofx_stream.seek(header_end, 0)
    ofx_stream = io.StringIO(ofx_stream.read())

    return ofx_stream, header


# TODO: close_tags fails if there are no closing tags already
#       Example:
#       >>> close_tags("<CODE>0<SEVERITY>INFO")
#       <CODE>0</CODE><SEVERITY>INFO
#       # Should be:
#       <CODE>0</CODE><SEVERITY>INFO</SEVERITY>
def close_tags(ofx_stream):
    """
    Closes any open tags, thus turning ofx_data into a valid XML stream.

    Also removes any processing tags "<?Processing_tag>" and comments
    "<!-- comment -->".

    Parameters:
    -----------
    ofx_stream : io.IOBase object
        The opened file object stream or StringIO stream of OFX data

    Returns :
    ---------
    new_stream : io.IOBase object
        A new stream with the same OFX data, but now with closed tags.

    Notes:
    ------
    This was taken from Jerry's ofxparse.OfxPreprocessedFile.__init__ code
    and modified to be cleaner and easier to read. The core algorithm remains
    the same.
    """
    # Read the file and create a new stream.
    ofx_string = ofx_stream.read()
    new_stream = io.StringIO()

    # We'll need some regex...
    opening_tag_re = re.compile(r"<([\w\.]+)>")     # <t_.x>   group: t_.x
    closing_tag_re = re.compile(r"</([\w\.]+)>")    # </t_.x>  group: t_.x
    token_re = re.compile(r"(</?[\w\.]+>)")         # <t_.x>   group: <t_.x>

    # Find all the closing tags
    closing_tags = [tag.upper()
                    for tag
                    in re.findall(closing_tag_re, ofx_string)]

    # Read all of the tokens
    tag_tokens = re.split(token_re, ofx_string)

    # Iterate through the tokens, writing them to the new string and adding
    # closing tags as needed.
    last_open_tag = None
    for num, token in enumerate(tag_tokens):
        # Determine what type of tag it is
        is_closing_tag = token.startswith("</")
        is_processing_tag = token.startswith("<?")
        is_cdata = token.startswith("<!")           # comment?
        is_tag = token.startswith("<") and not is_cdata
        is_open_tag = is_tag and not is_closing_tag and not is_processing_tag

        # if it's a tag
        if is_tag:
            if last_open_tag is not None:
                new_stream.write("</{}>".format(last_open_tag.strip()))
                last_open_tag = None
        if is_open_tag:
            tag_name = re.findall(opening_tag_re, token)[0]
            if tag_name.upper() not in closing_tags:
                last_open_tag = tag_name
        new_stream.write(token.strip())
    new_stream.seek(0)

    return new_stream


class Header(object):
    """
    An OFX Header object
    """
    def __init__(self, header_dict=None):
        self.ofxheader = None
        self.data = None
        self.version = None
        self.security = None
        self.encoding = None
        self.charset = None
        self.compression = None
        self.old_file_uid = None
        self.new_file_uid = None

        if header_dict is not None:
            self.load_dict(header_dict)

    def load_dict(self, header_dict):
        """
        Loads a header dictionary into the object
        """
        try:
            self.ofxheader = header_dict['OFXHEADER']
            self.data = header_dict['DATA']
            self.version = header_dict['VERSION']
            self.security = header_dict['SECURITY']
            self.encoding = header_dict['ENCODING']
            self.charset = header_dict['CHARSET']
            self.compression = header_dict['COMPRESSION']
            self.old_file_uid = header_dict['OLDFILEUID']
            self.new_file_uid = header_dict['NEWFILEUID']
        except KeyError:
            # TODO: fill in later
            raise KeyError


#class SignOnMessageResponse(object):
#    """
#    An OFX SignOnMessageResponse (SIGNONMSGSRSV1) object
#    """
#    def __init__(self):
#        self.sonrs = SignOnResponse()


class SignOnResponse(object):
    """
    An OFX SignOnResponse (SONRS) object

    ::

        "Every response must contain exactly one <SONRS> record."
            -- OFX Standard 2.1.1, Section 2.5.1
    """
    def __init__(self):
        self.status = Status()
        self.dt_server = None
        self.language = None
        self.fi = FinancialInstitution()    # XXX: Might remove?


class SignOnRequest(object):
    """
    An OFX SignOnRequest (SONRQ) object.

    ::

        Every Open Financial Exchange block contains exactly one <SONRQ>.
            -- OFX Standard 2.1.1, Section 2.5.1
    """
    def __init__(self):
        self.dt_client = None
        self.user_id = None
        self.user_password = None
        self.language = None
        self.fi = FinancialInstitution()    # XXX: Might remove?
        self.app_id = None
        self.app_version = None


#class SignUpMessageResponse(object):
#    """
#    An OFX SignUpMessageResponse (SIGNUPMSGSRSV1) object
#    """
#    # TODO: probably can remove
#    def __init__(self):
#        self.acct_info_trn_rs = AccountInfoTranscationResponse()


class AccountInfoTranscationResponse(object):
    """
    An OFX AccountInfoTranscationResponse (ACCTINFOTRNRS) object
    """
    def __init__(self):
        self.trnuid = None
        self.status = Status()
        self.clt_cookie = None
        self.acct_info_rs = AccountInfoResponse()


class AccountInfoResponse(object):
    """
    An OFX AccountInfoResponse (ACCTINFORS) object
    """
    def __init__(self):
        self.dt_acct_up = None
        self.account_info = []


class AccountInfo(object):
    """
    An OFX AccountInfo (ACCTINFO) object
    """
    def __init__(self):
        self.desc = None
        self.bank_account_info = BankAccountInfo()
        self.payment_acct_info = BankPaymentAccountInfo()


class BankAccountInfo(object):
    """
    An OFX BankAccountInfo (BANKACCTINFO) object
    """
    def __init__(self):
        self.bank_acct_from = BankAccountFrom()
        self.suptxdl = None
        self.xfersrc = None
        self.xferdest = None
        self.svcstatus = SVCStatus.unknown


class BankAccountFrom(object):
    """
    An OFX BankAccountFrom (BANKACCTFROM) object
    """
    def __init__(self):
        self.bank_id = None         # Routing number
        self.acct_id = None         # Account number
        self.acct_type = None


class BankPaymentAccountInfo(object):
    """
    An OFX BankPaymentAccountInfo (BPACCTINFO) object
    """
    def __init__(self):
        self.bank_acct_from = BankAccountFrom()
        self.svcstatus = SVCStatus.unknown


class CreditCardAccountInfo(object):
    """
    An OFX CreditCardAccountInfo (CCACCTINFO) object
    """
    def __init__(self):
        self.cc_acct_from = CreditCardAccountFrom()
        self.suptxdl = None
        self.xfersrc = None
        self.xferdest = None
        self.svcstatus = SVCStatus.unknown


class CreditCardAccountFrom(object):
    """
    An OFX CreditCardAccountFrom (CCACCTFROM) object
    """
    def __init__(self):
        self.acct_id = None

### #------------------------------------------------------------------------
### Misc.
### #------------------------------------------------------------------------

class Status(object):
    """
    An OFX Status object
    """
    def __init__(self):
        self.code = None
        self.severity = None
        self.message = None

#    def __str__(self):
#        return "OFXStatus: {}::{}::{}".format(self.code,
#                                              self.severity,
#                                              self.message)

    def __repr__(self):
        repr_str = "<{}.{} object `{}::{}::{}` at 0x{:>016}>"
        return repr_str.format(self.__class__.__module__,
                               self.__class__.__name__,
                               self.code,
                               self.severity,
                               self.message,
                               hex(id(self)).upper()[2:],
                               )


class SVCStatus(Enum):
    """
    An OFX SVC Status object (SVCSTATUS)
    """
    unknown = 0
    available = 1           # available, but not yet requested
    pending = 2             # requested, but not yet available
    active = 3              # in use


#class OFXDateTime(object):
#    """
#    An OFX DateTime object
#    """
#    # TODO: actually parse the date instead of leaving a string.
#    def __init__(self):
#        self.dt_string = None


class OFXBalance(object):
    """
    An OFX Balance object

    Parameters:
    -----------
    None

    Attributes:
    -----------
    balance : decimal.Decimal or None
    as_of_date : datetime.datetime or None
    """
    def __init__(self):
        self.balance = None
        self.as_of_date = None


### #------------------------------------------------------------------------
### Accounts
### #------------------------------------------------------------------------

class AccountType(Enum):
    """
    Account Types (ACCTTYPE)

    See page 600 of OFX Standard 2.1.1 (Section 16.1)
    """
    unknown = 0
    checking = 1
    savings = 2
    mnymarket = 3
    creditline = 4
    creditcrd = 5
    investment = 6
    retirement = 7


class BankAccountType(Enum):
    """
    Bank AccountTypes
    """
    unknown = 0
    checking = 1
    savings = 2

class Account(object):
    """
    An OFX account object.
    """
    def __init__(self):
        self.statement = None
        self.routing_number = ''
        self.branch_id = ''
        self.account_type = ''
        self.institution = None
        self.type = AccountType.unknown

        self.desc = None
        self.account_id = None
        self.suptxdl = None
        self.xfersrc = None
        self.xferdest = None
        self.svcstatus = None
        # Used for error tracking
        self.warnings = []


class InvestmentAccount(Account):
    """
    An OFX Investment Account object
    """
    def __init__(self):
#        super(InvestmentAccount, self).__init__()
        super().__init__()
        self.brokerid = ''

class BankAccount(Account):
    """
    An OFX Bank Account object
    """
    def __init__(self):
        super().__init__()
        self.bank_id = None
        self.bank_account_type = None


class CreditCardAccount(Account):
    """
    And OFX Credit Card Account object
    """
    def __init__(self):
        super().__init__()


### #------------------------------------------------------------------------
### Statements
### #------------------------------------------------------------------------

class OFXStatement(object):
    """
    An OFX Statement object
    """
    def __init__(self):
        self.transactions = None
        self.curdef = None
        self.bank_acct_from = None
        self.dtstart = None
        self.dtend = None
        self.ledger_balance = None
        self.available_balance = None


class BankStatement(OFXStatement):
    """
    An OFX Bank (standard) Statement object
    """
    def __init__(self):
        super().__init__()


class CreditCardStatement(OFXStatement):
    """
    An OFX Credit Card Statement Object
    """
    def __init__(self):
        super().__init__()


class InvestmentStatement(OFXStatement):
    """
    An OFX Investment Statement object
    """
    def __init__(self):
        super().__init__()


### #------------------------------------------------------------------------
### Transactions
### #------------------------------------------------------------------------

class TransactionType(Enum):
    unknown = 0
    Credit = 1
    Debit = 2
    Interest = 3
    Dividend = 4
    Fee = 5
    ServiceCharge = 6
    Deposit = 7
    ATM = 8
    PointOfSale = 9
    Transfer = 10
    Check = 11
    Payment = 12
    Cash = 13
    DirectDeposit = 14
    DirectDebit = 15
    RepeatPayment = 16
    Other = 17


class OFXTransaction(object):
    """
    An OFX Tranaction object
    """
    pass


class BankTransaction(OFXTransaction):
    """
    An OFX Bank (checking, savings, other?) Transaction object.
    """
    def __init__(self):
        super().__init__()
        self.trntype = TransactionType.unknown
        self.dtposted = None
        self.dtuser = None
        self.trnamt = None
        self.fitid = None
        self.checknum = None
        self.name = None
        self.memo = None


class CreditCardTransaction(OFXTransaction):
    """
    An OFX Credit Card Transaction object
    """
    def __init__(self):
        super().__init__()

class InvestmentTransaction(OFXTransaction):
    """
    An OFX Investment Transaction object
    """
    def __init__(self):
        super().__init__()


class FinancialInstitution(object):
    """
    An OFX Financial Institution object.

    Gets filled in by `FI.ORG` and `FI.FID`
    """
    def __init__(self):
        self.org = None
        self.fid = None



EXAMPLE_OFX_ACCOUNT_LIST = (b"""
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
                    <BANKACCTINFO>"""          # Bank Account Info
b"""
                        <BANKACCTFROM>
                            <BANKID>routing_num
                            <ACCTID>bank_account_num
                            <ACCTTYPE>CHECKING
                        </BANKACCTFROM>
                        <SUPTXDL>Y
                        <XFERSRC>Y
                        <XFERDEST>Y
                        <SVCSTATUS>ACTIVE
                    </BANKACCTINFO>
                    <BPACCTINFO>"""         # Bank *Payment* Account Info
b"""
                        <BANKACCTFROM>
                            <BANKID>routing_num
                            <ACCTID>bank_account_num
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
""")


EXAMPLE_OFX_ACCOUNT_LIST_CLOSED = """
<OFX>
    <SIGNONMSGSRSV1>
        <SONRS>
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</INFO>
            </STATUS>
            <DTSERVER>20150520232950.608[0:GMT]</DTSERVER>
            <LANGUAGE>ENG</LANGUAGE>
            <FI>
                <ORG>FI_ORGNAME</ORG>
                <FID>123456</FID>
            </FI>
        </SONRS>
    </SIGNONMSGSRSV1>
    <SIGNUPMSGSRSV1>
        <ACCTINFOTRNRS>
            <TRNUID>trnuid</TRNUID>
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
            <CLTCOOKIE>4</CLTCOOKIE>
            <ACCTINFORS>
                <DTACCTUP>20150520232957.222[0:GMT]</DTACCTUP>
                <ACCTINFO>
                    <DESC>Checking</DESC>
                    <BANKACCTINFO>
                        <BANKACCTFROM>
                            <BANKID>routing_num</BANKID>
                            <ACCTID>bank_account_num</ACCTID>
                            <ACCTTYPE>CHECKING</ACCTYPE>
                        </BANKACCTFROM>
                        <SUPTXDL>Y</SUPTXDL>
                        <XFERSRC>Y</XFERSRC>
                        <XFERDEST>Y</XFERDEST>
                        <SVCSTATUS>ACTIVE</SVCSTATUS>
                    </BANKACCTINFO>
                    <BPACCTINFO>
                        <BANKACCTFROM>
                            <BANKID>routing_num</BANKID>
                            <ACCTID>bank_account_num</ACCTID>
                            <ACCTTYPE>CHECKING</ACCTYPE>
                        </BANKACCTFROM>
                        <SVCSTATUS>ACTIVE</SVCSTATUS>
                    </BPACCTINFO>
                </ACCTINFO>
                <ACCTINFO>
                    <DESC>Visa</DESC>
                    <CCACCTINFO>
                        <CCACCTFROM>
                            <ACCTID>credit_card_num</ACCTID>
                        </CCACCTFROM>
                        <SUPTXDL>Y</SUPTXDL>
                        <XFERSRC>Y</XFERSRC>
                        <XFERDEST>Y</XFERDEST>
                        <SVCSTATUS>ACTIVE</SVCSTATUS>
                    </CCACCTINFO>
                </ACCTINFO>
            </ACCTINFORS>
        </ACCTINFOTRNRS>
    </SIGNUPMSGSRSV1>
</OFX>
"""

EXAMPLE_OFX_ACCOUNT_LIST_OPEN = """
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
</OFX>
"""


def main():
    """ Code to run when module called directly, just some quick checks. """
    docopt(__doc__, version="0.0.1")    # TODO: pull VERSION from __init__
    file = "tests\\data\\rs_investments.ofx"

    with open(file, 'r') as openf:
        a = ParseOFX(openf)
    print(a.fi.fid)
    print(a.statement)
    print(a.statement.transactions)
    for trans in a.statement.transactions:
        print(trans.fitid)
    print(a.statement.available_balance.balance)
    print(a.statement.ledger_balance.balance)


#    a = ParseOFX(EXAMPLE_OFX_ACCOUNT_LIST)
#    a = ParseOFX(str(EXAMPLE_OFX_ACCOUNT_LIST, encoding='utf-8'))
#    with open(file, 'rb') as openf:
#        a = ParseOFX(openf)
#    b = a.parse()
#    print(a)
#    print("============")
#    print(a.sonrs)
#    print(a.sonrs.status)
#    print(a.sonrs.dt_server)
#    print(a.fi)
#    print(a.accounts)
#    print(a.accounts[1].account_type)
#    acct = a.accounts[1]
#
#    print(acct.desc)
#    print(acct.account_id)
#    print(acct.suptxdl)
#    print(acct.xfersrc)
#    print(acct.xferdest)
#    print(acct.svcstatus)
#    print(acct.dt_acct_up)
#    print(a.header)
#
#    soup = BeautifulSoup("""
#            <STATUS>
#                <CODE>0</SCODES>
#                <SEVERITY>INFO</SSEVERITY>
#            </STATUS>
#            """, 'xml')
#    result = parse_status(soup)
#    print("`{}`".format(result.severity))

#    stream = io.StringIO(str(EXAMPLE_OFX_ACCOUNT_LIST, encoding='utf-8'))
##    stream = io.StringIO(EXAMPLE_OFX_ACCOUNT_LIST_CLOSED)
#    _, d = strip_header(stream)
#    print(d)

#    print("========================")
#    stream = io.StringIO(EXAMPLE_OFX_ACCOUNT_LIST_OPEN)
#    new = close_tags(stream)
#    print(new.read())
#    new.seek(0)
#    soup = BeautifulSoup(new, 'xml')
#    print(soup.prettify())

#    print(a.header)

#    import ofxparse
#    with open(file, 'rb') as openf:
#        print(type(openf))
#        print(isinstance(openf, io.IOBase))
#        a = ofxparse.OfxParser.parse(openf)
#    print(a)
#    print(a.accounts)
#    b = a.accounts[0]
#    print(b.number)

#    stream = io.StringIO(EXAMPLE_OFX_ACCOUNT_LIST.decode('utf-8'))
#    a = ofxparse.OfxParser.parse(stream)
#    print(a.accounts)


if __name__ == "__main__":
    main()
#    pass

