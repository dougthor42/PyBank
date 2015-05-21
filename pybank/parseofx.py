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
import os.path as osp
from enum import Enum

# Third-Party
from docopt import docopt
from bs4 import BeautifulSoup

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


class OFX(object):
    """

    """
    pass


class ProceesOFXData(object):
    """
    Processes the OFX data into a valid XML schema
    """
    pass


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

    Public Attributes:
    ------------------
    stuff

    Public Methods:
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

        # convert ofx_data to a stream
        # TODO: Handle closing of opened streams
        if type(ofx_data) == str:
            ofx_data = io.StringIO(ofx_data, newline=self.newline)
        elif type(ofx_data) == bytes:
            ofx_data = str(ofx_data, encoding='utf-8')
            ofx_data = io.StringIO(ofx_data, newline=self.newline)
        elif type(ofx_data) == io.BufferedReader:
            pass
        elif type(ofx_data) == io.StringIO:
            pass
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
        self.ofx = OFX()

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

        # Find the single Sign On Response
        self.ofx_sonrs = self.soup.find("SONRS")
        if self.ofx_sonrs is not None:
            self._parse_sonrs()

        # Find all of the Statement Responses
        # note I could use soup("STMTRS"); its the same as soup.findAll()
        self.stmtrs = self.soup.findAll("STMTRS")
        if len(self.stmtrs) != 0:                       # I prefer explicit
            self._parse_statement_response()

        # Find all of the Credit Card Statement Response
        self.ccstmtrs = self.soup.findAll("CCSTMTRS")
        if len(self.ccstmtrs) != 0:
            self._parse_statement_response()

        # Find all of the Investment Statement Response
        self.invstmtrs = self.soup.findAll("INVSTMTRS")
        if len(self.invstmtrs) != 0:
            self._parse_statement_response()

        # Find the Account Info Response
        self.acctinfors = self.soup.find("ACCTINFORS")
        if self.acctinfors is not None:
            self._parse_acct_info_response()

        # Find the Financial Institution
        self.fi = self.soup.find("FI")
        if self.fi is not None:
            self._parse_financial_institution()

    def _parse_sonrs(self):
        """
        Parses the Sign On Response (SONRS)
        """
        self.sonrs = SignOnResponse()
        self.sonrs.status = parse_status(self.ofx_sonrs)
        self.sonrs.dt_server = parse_datetime(self.ofx_sonrs)
        self.sonrs.language = self.soup.find('LANGUAGE').contents[0]
#        self.sonrs.fi = self._parse_financial_institution()

    def _parse_statement_response(self):
        """
        Parses the Statement Response (STMTRS)
        """
        pass

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
        Parses the Account Information Response (ACCTINFORS)
        """
        pass

    def _parse_financial_institution(self):
        """
        Parses the Financial Institution (FI)
        """
        pass


def parse_status(soup):
    """
    Slurps up the OFX Status from the soup.
    """
    status = Status()
    status.code = int(soup.find('CODE').contents[0])
    status.severity = soup.find('SEVERITY').contents[0]
    try:
        status.message = soup.find('MESSAGE').contents[0]
    except AttributeError:
        status.message = None

    return status


def parse_datetime(soup):
    """
    Parses the OFX datetime

    Tries DTACCTUP, DTSTART, DTCLIENT, DTSERVER

    ::

        There is one format for representing dates, times, and time
        zones. The complete form is:

        YYYYMMDDHHMMSS.XXX [gmt offset[:tz name]]
            -- OFX Standard 2.1.1, Section 3.2.8.1

    This will need to handle partial times too.

    For now, just grab the string.
    """
    dt_tags = ["DTACCTUP", "DTCLIENT", "DTSERVER", "DTSTART"]
    ofx_dt = OFXDateTime()
    for tag in dt_tags:
        try:
            ofx_dt.dt_string = soup.find(tag).contents[0]
            return ofx_dt
        except AttributeError:
            continue
    else:
        raise AttributeError("Datetime tag not found")


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
    header_end = header_str.find('<OFX>')
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


class SignOnMessageResponse(object):
    """
    An OFX SignOnMessageResponse (SIGNONMSGSRSV1) object
    """
    def __init__(self):
        self.sonrs = SignOnResponse()


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


class SignUpMessageResponse(object):
    """
    An OFX SignUpMessageResponse (SIGNUPMSGSRSV1) object
    """
    # TODO: probably can remove
    def __init__(self):
        self.acct_info_trn_rs = AccountInfoTranscationResponse()


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
        self.svcstatus = None


class BankAccountFrom(object):
    """
    An OFX BankAccountFrom (BANKACCTFROM) object
    """
    def __init__(self):
        self.bank_id = None         # Account number
        self.acct_id = None         # Routing number
        self.acct_type = None


class BankPaymentAccountInfo(object):
    """
    An OFX BankPaymentAccountInfo (BPACCTINFO) object
    """
    def __init__(self):
        self.bank_acct_from = BankAccountFrom()
        self.svcstatus = None


class CreditCardAccountInfo(object):
    """
    An OFX CreditCardAccountInfo (CCACCTINFO) object
    """
    def __init__(self):
        self.cc_acct_from = CreditCardAccountFrom()
        self.suptxdl = None
        self.xfersrc = None
        self.xferdest = None
        self.svcstatus = None


class CreditCardAccountFrom(object):
    """
    An OFX CreditCardAccountFrom (CCACCTFROM) object
    """
    def __init__(self):
        self.acct_id = None


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

    # TODO: make __repr__ look standard
    def __repr__(self):
        repr_str = "<{}.{} object `{}::{}::{}` at 0x{}>"
        return repr_str.format(self.__class__.__module__,
                               self.__class__.__name__,
                               self.code,
                               self.severity,
                               self.message,
                               hex(id(self)).upper()[2:],
                               )


class OFXDateTime(object):
    """
    An OFX DateTime object
    """
    def __init__(self):
        self.dt_string = None


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
                            <BANKID>bankid_bank_account_num
                            <ACCTID>acctid_routing_num
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
                            <BANKID>bankid_bank_account_num</BANKID>
                            <ACCTID>acctid_routing_num</ACCTID>
                            <ACCTTYPE>CHECKING</ACCTYPE>
                        </BANKACCTFROM>
                        <SUPTXDL>Y</SUPTXDL>
                        <XFERSRC>Y</XFERSRC>
                        <XFERDEST>Y</XFERDEST>
                        <SVCSTATUS>ACTIVE</SVCSTATUS>
                    </BANKACCTINFO>
                    <BPACCTINFO>
                        <BANKACCTFROM>
                            <BANKID>bankid_bank_account_num</BANKID>
                            <ACCTID>acctid_routing_num</ACCTID>
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
    docopt(__doc__, version=VERSION)
    file = "example_ofx_acct_list.ofx"
    a = ParseOFX(EXAMPLE_OFX_ACCOUNT_LIST)
#    a = ParseOFX(str(EXAMPLE_OFX_ACCOUNT_LIST, encoding='utf-8'))
#    with open(file, 'rb') as openf:
#        a = ParseOFX(openf)
#    b = a.parse()
#    print(a)
    print("============")
    print(a.sonrs)
    print(a.sonrs.status)
    print(a.sonrs.dt_server)

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
