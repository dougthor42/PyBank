# -*- coding: utf-8 -*-
"""
Base for the SQLAlchemy Object Relational Mapper (ORM).

Contains all of the default table constructors used by PyBank.

Created on Sun Dec  6 20:31:06 2015

Usage:
    sa_orm_base.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""
# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
import logging
import decimal
from decimal import Decimal
import datetime
import contextlib
import warnings

# Third Party
import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.ext import compiler as sa_compiler
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import CreateTable
from sqlalchemy import text as saText

# Package / Application
try:
    # Imports used by unit test runners
    from . import (__project_name__,
                   __version__,
                   )
    from . import utils
    logging.debug("Imports for orm.py complete (Method: UnitTest)")
except SystemError:
    try:
        # Imports used by Spyder
        from __init__ import (__project_name__,
                              __version__,
                              )
        import utils
        logging.debug("Imports for orm.py complete (Method: Spyder IDE)")
    except ImportError:
         # Imports used by cx_freeze
        from pybank import (__project_name__,
                            __version__,
                            )
        from pybank import utils
        logging.debug("Imports for orm.py complete (Method: Executable)")


# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------
Base = declarative_base()
engine = sa.create_engine('sqlite:///:memory:', echo=False)


# ---------------------------------------------------------------------------
### Items needed to create a view in SQLAlchemy
# See http://stackoverflow.com/a/9769411/1354930
#     http://stackoverflow.com/a/9597404/1354930
#     https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/Views
# ---------------------------------------------------------------------------
class CreateView(sa.schema.DDLElement):
    def __init__(self, name, selectable):
        self.name = name
        self.selectable = selectable


class DropView(sa.schema.DDLElement):
    def __init__(self, name):
        self.name = name


# SQLite ####################################################################
@sa_compiler.compiles(CreateView, 'sqlite')
def compile(element, compiler, **kw):
    sql_str = "CREATE VIEW IF NOT EXISTS {} AS {}"
    process_compiler = compiler.sql_compiler.process(element.selectable)
    return sql_str.format(element.name, process_compiler)


@sa_compiler.compiles(DropView, 'sqlite')
def compile(element, compiler, if_exists=False, **kw):
    sql_str = "DROP VIEW IF EXISTS {}"
    return sql_str.format(element.name)


# Other Databases ###########################################################
@sa_compiler.compiles(CreateView)
def compile(element, compiler, **kw):
    sql_str = "CREATE VIEW {} AS {}"
    process_compiler = compiler.sql_compiler.process(element.selectable)
    return sql_str.format(element.name, process_compiler)


@sa_compiler.compiles(DropView)
def compile(element, compiler, if_exists=False, **kw):
    sql_str = "DROP VIEW {}"
    return sql_str.format(element.name)


def view(name, metadata, selectable):
    t = sa.sql.table(name)

    for c in selectable.c:
        c._make_proxy(t)

    # TODO: convert to event.listen
    warnings.simplefilter('ignore', DeprecationWarning)
    CreateView(name, selectable).execute_at('after-create', metadata)
    DropView(name).execute_at('before-drop', metadata)
    warnings.resetwarnings()

#    event.listen(metadata, 'after-create', CreateView(name, selectable))
#    event.listen(metadata, 'before-drop', DropView(name))

    return t


# ---------------------------------------------------------------------------
### Helper Classes
# ---------------------------------------------------------------------------
class SqliteNumeric(sa.types.TypeDecorator):
    """
    Custom-made Numeric type specifically for SQLite.

    Converts a Decimal to a string when writing to the database, and converts
    it back to a Decimal when reading.

    See http://stackoverflow.com/a/10386911/1354930
    """
    impl = sa.types.String

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(sa.types.VARCHAR(30))

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            logging.info("Value is None")
            return None
        try:
            return Decimal(value)
        except decimal.InvalidOperation:
            logging.error("decimal.InvalidOperation on value `%s`", value)
            return Decimal('0.00')


# ---------------------------------------------------------------------------
### Event Handling
# ---------------------------------------------------------------------------
# I don't really need events if I'm going with what I was doing earlier:
#   Decrypt the file to a temp one, do all actions on that, then periodically
#   re-encrypt with the new data.
#def on_checkout(dbapi_conn, connection_rec, connection_proxy):
#    print("handling on_checkout")
#
#
#def on_connect(dbapi_conn, connection_record):
#    print('handling on_connect')


#event.listen(engine, 'checkout', on_checkout)
#event.listen(engine, 'connect', on_connect)


# ---------------------------------------------------------------------------
### Functions required by ORM classes
# ---------------------------------------------------------------------------
def create_ledger_view():
    """ """
    # TODO: do I want outer joins?
    oj = sa.outerjoin(Transaction, Payee)
    oj = sa.outerjoin(oj, Category,
                      Category.category_id == Transaction.category_id)
    oj = sa.outerjoin(oj, TransactionLabel,
                      TransactionLabel.transaction_label_id == Transaction.transaction_label_id)
    oj = sa.outerjoin(oj, DisplayName,
                      DisplayName.display_name_id == Payee.display_name_id)
    oj = sa.outerjoin(oj, Account,
                      Account.account_id == Transaction.account_id)
    oj = sa.outerjoin(oj, Memo,
                      Memo.memo_id == Transaction.memo_id)

    func = sa.sql.func

    select = sa.select([Transaction.transaction_id,
                        Transaction.date,
                        Transaction.account_id,
                        Account.name.label('AccountName'),
                        Transaction.enter_date,
                        Transaction.check_num,
                        func.coalesce(DisplayName.name,
                                      Payee.name).label('Payee'),
                        Payee.name.label('DownloadedPayee'),
                        TransactionLabel.value.label('TransactionLabel'),
                        Category.category_id.label('Category'),
                        Memo.text.label('Memo'),
                        Transaction.amount.label('amount'),
                        ]
                       )

    selectable = select.select_from(oj)

    engine.execute(sa.text("DROP VIEW IF EXISTS 'ledger_view'"))

    ledger_view = view('ledger_view',
                       Base.metadata,
                       selectable)

    return ledger_view, selectable


# ---------------------------------------------------------------------------
### ORM Classes
# ---------------------------------------------------------------------------
class Account(Base):
    """
    Account

    Contains the accound_id, account_num, user_name, institution_id,
    and account_group_id.

    """
    __tablename__ = 'account'

    account_id = sa.Column(sa.Integer, primary_key=True)
    account_num = sa.Column(sa.String, nullable=False)
    name = sa.Column(sa.String, nullable=False)
    user_name = sa.Column(sa.String, nullable=False)
    institution_id = sa.Column(sa.Integer,
                               sa.ForeignKey('institution.institution_id'))
    account_group_id = sa.Column(sa.Integer,
                                 sa.ForeignKey('account_group.account_group_id'))

    institution = relationship('Institution')
    account_group = relationship('AccountGroup')

    def __str__(self):
        return "{}: {}".format(self.account_id, self.account_num)


class AccountGroup(Base):
    """
    AccountGroup

    not currently used.

    """
    __tablename__ = 'account_group'

    account_group_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)

    def __str__(self):
        return "{}: {}".format(self.account_group_id, self.name)

class Category(Base):
    """
    Category

    Uses Adjacency List Model. See
    http://mikehillyer.com/articles/managing-hierarchical-data-in-mysql/

    Contains the category_id, name, and parent.
    """
    __tablename__ = 'category'

    category_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    parent = sa.Column(sa.Integer, sa.ForeignKey('category.category_id'))

    children = relationship("Category")

    def __str__(self):
        return "{}: {}".format(self.category_id, self.name)

class DisplayName(Base):
    """
    DisplayName

    Contains the display_name_id and name.

    """
    __tablename__ = 'display_name'

    display_name_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Integer)

    def __str__(self):
        return "{}: {}".format(self.display_name_id, self.name)

class Institution(Base):
    """
    Institution

    Contains the institution_id, name, and ofx_id

    """
    __tablename__ = 'institution'

    institution_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    fid = sa.Column(sa.String)
    org = sa.Column(sa.String)
    url = sa.Column(sa.String)
    broker = sa.Column(sa.String)

    def __str__(self):
        return "{}: {}".format(self.institution_id, self.name)

class Memo(Base):
    """
    Memo

    Contains the memo_id and text.

    """
    __tablename__ = 'memo'

    memo_id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.String)

#    def __repr__(self):
#        return "{}: {}".format(self.memo_id, self.text)

    def __str__(self):
        return "{}: {}".format(self.memo_id, self.text)

class Payee(Base):
    """
    Payee

    Contains the payee_id, name, display_name_id, and category_id.

    """
    __tablename__ = 'payee'

    payee_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    display_name_id = sa.Column(sa.Integer,
                                sa.ForeignKey('display_name.display_name_id'),
                                )
    category_id = sa.Column(sa.Integer,
                            sa.ForeignKey('category.category_id'),
                            )

    display_name = relationship('DisplayName')
    category = relationship('Category')

    def __str__(self):
        return "{}: {}".format(self.payee_id, self.name)

class Transaction(Base):
    """
    Transaction

    Contains the transaction_id, account_id, date, enter_date, check_num,
    amount, payee_id, category_id, transaction_label_id, memo_id, and fitid.

    """
    __tablename__ = 'transaction'

    transaction_id = sa.Column(sa.Integer, primary_key=True)
    account_id = sa.Column(sa.Integer, sa.ForeignKey('account.account_id'))
    date = sa.Column(sa.Date)
    enter_date = sa.Column(sa.Date)
    check_num = sa.Column(sa.Integer)
    amount = sa.Column(SqliteNumeric)
    payee_id = sa.Column(sa.Integer, sa.ForeignKey('payee.payee_id'))
    category_id = sa.Column(sa.Integer, sa.ForeignKey('category.category_id'))
    transaction_label_id = sa.Column(sa.Integer, sa.ForeignKey('transaction_label.transaction_label_id'))
    memo_id = sa.Column(sa.Integer, sa.ForeignKey('memo.memo_id'))
    fitid = sa.Column(sa.Integer)

    payee = relationship('Payee')
    category = relationship('Category')
    transaction_label = relationship('TransactionLabel')
    memo = relationship('Memo')

    def __str__(self):
        return "{}: {}".format(self.transaction_id, self.amount)

class TransactionLabel(Base):
    """
    TransactionLabel

    Contains the transaction_label_id and name.

    """
    __tablename__ = 'transaction_label'

    transaction_label_id = sa.Column(sa.Integer, primary_key=True)
    value = sa.Column(sa.String)

    def __str__(self):
        return "{}: {}".format(self.transaction_label_id, self.name)


class LedgerView(Base):
    """
    LedgerView

    Stuff
    """
    __tablename = "ledger_view"
    __table__, selectable = create_ledger_view()

#    def __str__(self):
#        return "{}: {}".format(self.category_id, self.name)


# ---------------------------------------------------------------------------
### Create the metadata and Session
# ---------------------------------------------------------------------------
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


# ---------------------------------------------------------------------------
### ORM Query Functions
# ---------------------------------------------------------------------------
@utils.logged
def query_ledger_view():
    logging.info("Quering Ledger View")
    return session.query(LedgerView).all()


@utils.logged
def query_category():
    logging.info("Querying `Category` table")
    return session.query(Category).all()

# ---------------------------------------------------------------------------
### ORM Insert Functions
# ---------------------------------------------------------------------------
def insert_account_group(name):
    logging.debug("inserting '{}' to AccountGroup".format(name))
    acct_group = AccountGroup(name=name)
    session.add(acct_group)


def insert_account(name, acct_num, user, institution_id, acct_group=None):
    logging.debug("inserting '{}' to Account".format(name))
    acct = Account(account_num=acct_num,
                   name=name,
                   user_name=user,
                   institution_id=institution_id,
                   account_group_id=acct_group)
    session.add(acct)


def insert_category(name, parent):
    logging.debug("inserting '{}' to Category".format(name))
    cat = Category(name=name, parent=parent)
    session.add(cat)


def insert_display_name(name):
    logging.debug("inserting '{}' to DisplayName".format(name))
    display_name = DisplayName(name=name)
    session.add(display_name)


def insert_institution(name, fid=None, org=None, url=None, broker=None):
    logging.debug("inserting '{}' to Institution".format(name))
    institution = Institution(name=name,
                              fid=fid,
                              org=org,
                              url=url,
                              broker=broker)
    session.add(institution)


def insert_memo(text):
    logging.debug("inserting '{}' to Memo".format(text))
    memo = Memo(text=text)
    session.add(memo)


def insert_payee(name, display_name_id=None, category_id=None):
    logging.debug("inserting '{}' to Payee".format(name))
    payee = Payee(name=name,
                  display_name_id=display_name_id,
                  category_id=category_id)
    session.add(payee)


@utils.logged
def insert_transaction(insert_dict):
    logging.info("inserting item to Transaction")

    date_fmt = '%Y-%m-%d'

    # make sure that the date and enter_date columns are datetime.Datetime
    # objects
    dt = datetime.datetime
    try:
        insert_dict['date'] = dt.strptime(insert_dict['date'], date_fmt).date()
    except KeyError:
        pass
    except ValueError:
        logging.error("Invalid date format: `%s`", insert_dict['date'])
    except:
        logging.error("An unknown error occured")
        raise

    trans = Transaction(**insert_dict)
    session.add(trans)


def insert_transaction_label(value):
    logging.debug("inserting '{}' to AccountGroup".format(value))
    trans_label = TransactionLabel(value=value)
    session.add(trans_label)


@utils.logged
def insert_ledger(*args, **kwargs):
    """
    Handles inserting items into the ledger

    Every string needs to be matched to its ID in its table. If any new
    values are found, those need to 1st be added to the respective table.
    """
    logging.info("Inserting values into ledger")
    logging.info("(not really because the function is not implemented yet)")
    pass


# ---------------------------------------------------------------------------
### ORM Insert Functions
# ---------------------------------------------------------------------------
@utils.logged
def update_transaction(trans_id, update_dict):
    """
    """
    logging.info("Updating transaction")

    query = session.query(Transaction).filter_by(transaction_id=trans_id)
    query.update(update_dict)


@utils.logged
def update_ledger(*args, **kwargs):
    """
    """
    logging.info("Updating ledger values")
    logging.info("But not really because this function is not done yet")
    pass

# ---------------------------------------------------------------------------
### Other Functions
# ---------------------------------------------------------------------------
@utils.logged
def create_database():

#    engine = sa.create_engine(engine_str, echo=False)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    return engine, session


@utils.logged
def copy_to_sa(engine, session, dump):
    """
    We know that our SQLite database will have the same structure as
    the SQLAlchemy ORM. So we just have to iterate through everything, copying
    data over.

    The engine and the session must already be created.

    Parameters:
    -----------
    engine: SQLAlchemy.engine.Engine object
        The engine to work on

    session: SQLAlchemy.orm.session.Session object
        The session to work on

    dump : iterable
        A list or generator object that contains strings for table creation
        and data. Typically the result of `sqlite_iterdump()` or
        `sqlite3.iterdump()`.

    Returns:
    --------
    None?
    """
    for sql in dump:
        if sql.startswith("INSERT"):
            # "None" is not recognized by SQLite when executing SQL, so we
            # need to repalce it with NULL.
            sql = sql.replace("None", "NULL")
            engine.execute(saText(sql))


@utils.logged
def sqlite_iterdump(engine, session):
    """
    Mimmics SQLites' `iterdump()` function.

    Returns an iterator to dump the database in an SQL text format.

    The only (known) difference is that row data values have spaces
    between columns while sqlite's `iterdump()` does not.

    **NOTE: THIS FUNCTION IS SPECIALISED FOR PYBANK AND THE 1 VIEW THAT
    IT CONTAINS. IT WILL MOST NOT WORK ON A GENERIC DATABASE.**

    The SQLAlchemy declaritive base class `Base` must be imported already.

    Parameters:
    -----------
    engine: SQLAlchemy.engine.Engine object
        The engine to work on

    session: SQLAlchemy.orm.session.Session object
        The session to work on

    Returns:
    --------
    sql : iterator
        The dump of the SQL.
    """
    tables = Base.metadata.tables
    n = 0

    # start off by yielding the begin trans statement.
    if n == 0:
        n = 1
        yield "BEGIN TRANSACTION;"

    # then move to yielding the tables and their data, in order
    # Note: sorting tables.items() removes the benefit of it being a
    #       generator. However, I doubt many DBs will have > 10000 tables...
    if n == 1:
        for name, table in sorted(tables.items()):
            logging.debug("dumping table %s", name)
            yield str(CreateTable(table).compile(engine)).strip() + ";"

            data = session.query(table).all()
            for row in data:
                row = list(row)     # needs to be mutable

                row = [str(x) if isinstance(x, Decimal)
                       else x.isoformat() if isinstance(x, datetime.date)
#                       else "" if x is None
                       else x for x in row]

                row = tuple(row)    # back to tuple because I use its parens
                                    # instead of adding my own parentheses.
                yield 'INSERT INTO "{}" VALUES{};'.format(name, row)
        n = 2

    # end by yielding the view and commit statements.
    if n == 2:
        n = 3
        view = CreateView("ledger_view", LedgerView.selectable)
        yield str(view.compile(engine)) + ";COMMIT;"


def _test_iterdump_loop(dump_file):
    """
    Test the iterdump -> load -> iterdump loop.

    An iterdump file must already exist. sa_orm_base must be set up to
    be an in-memory database.
    """
    engine, session = create_database()

    with open(dump_file, 'r') as openf:
        data = openf.read()
        data = data.split(';')
        copy_to_sa(engine, session, data)

    dump = "".join(line for line in sqlite_iterdump(engine, session))
    dump = dump.encode('utf-8')
    with open("C:\\WinPython34\\projects\\github\\PyBank\\pybank\\tests\\data\\_TestDB_generated_dump.txt", 'wb') as openf:
        openf.write(dump)

    session.close()
    engine.dispose()


def dump_to_file(engine, session, file):
    """ """
    dump = list(sqlite_iterdump(engine, session))
    dump = "".join(line for line in dump)
    dump = dump.encode('utf-8')

    with open(file, 'wb') as openf:
        openf.write(dump)

# ---------------------------------------------------------------------------
### Run as module
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    dump = list(sqlite_iterdump(engine, session))
    dump = "".join(line for line in dump)
    dump = dump.encode('utf-8')

    with open("temp_dump_file.txt", 'wb') as openf:
        openf.write(dump)
