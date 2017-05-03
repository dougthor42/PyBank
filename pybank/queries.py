# -*- coding: utf-8 -*-
"""
Queries used by PyBank.
"""
# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
import logging
from decimal import Decimal
import datetime

# Third Party
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateTable
from sqlalchemy import text as saText

# Package / Application
from . import utils
from .orm import session, Base, engine
from .orm import CreateView
from .orm import (          # Tables
    Account,
    AccountGroup,
    Category,
    DisplayName,
    Institution,
    LedgerView,
    Memo,
    Payee,
    Transaction,
    TransactionLabel,
)


@utils.logged
def query_ledger_view():
    logging.info("Quering Ledger View")
    return session.query(LedgerView).all()


@utils.logged
def query_category():
    logging.info("Querying `Category` table")
    return session.query(Category).all()


def insert_account_group(name):
    """
    Insert a new account group.

    Parameters
    ----------
    name : str
        The name of the account group to add.

    Returns
    -------
    None
    """
    logging.debug("inserting '{}' to AccountGroup".format(name))
    acct_group = AccountGroup(name=name)
    session.add(acct_group)


def insert_account(name, acct_num, user, institution_id, acct_group=None):
    """
    Insert a new account.

    Parameters
    ----------
    name : str
        The name of the account to add.
    acct_num : str
        The account number.
    user : str
        The user name for the bank.
    institution_id : int
        The ``id`` of the institution to link this account to.
    acct_group : int, optional
        What group this account belongs to.

    Returns
    -------
    None
    """
    logging.debug("inserting '{}' to Account".format(name))
    acct = Account(account_num=acct_num,
                   name=name,
                   user_name=user,
                   institution_id=institution_id,
                   account_group_id=acct_group)
    session.add(acct)


def insert_category(name, parent):
    """
    Insert a new category.

    Parameters
    ----------
    name : str
        The name of the category to add.
    parent : int
        The ``id`` of the parent category that this category belongs to.

    Returns
    -------
    None
    """
    logging.debug("inserting '{}' to Category".format(name))
    cat = Category(name=name, parent=parent)
    session.add(cat)


def insert_display_name(name):
    """
    Insert a new display name.

    Parameters
    ----------
    name : str
        The name of the display name to add.

    Returns
    -------
    None
    """
    logging.debug("inserting '{}' to DisplayName".format(name))
    display_name = DisplayName(name=name)
    session.add(display_name)


def insert_institution(name, fid=None, org=None, url=None, broker=None):
    """
    Insert a new institution.

    Parameters
    ----------
    name : str
        The name of the institution to add.
    fid : str, optional
        The Financial Institution ID defined by OFX.
    url : str, optional
        The OFX download url.
    broker : str, optional
        ???

    Returns
    -------
    None
    """
    logging.debug("inserting '{}' to Institution".format(name))
    institution = Institution(name=name,
                              fid=fid,
                              org=org,
                              url=url,
                              broker=broker)
    session.add(institution)


def insert_memo(text):
    """
    Insert a new memo.

    Parameters
    ----------
    text : str
        The text of the memo.

    Returns
    -------
    None
    """
    logging.debug("inserting '{}' to Memo".format(text))
    memo = Memo(text=text)
    session.add(memo)


def insert_payee(name, display_name_id=None, category_id=None):
    """
    Insert a new payee.

    Parameters
    ----------
    name : str
        The name of the payee to add.
    display_name_id : int, optional
        The default display name to be shown for this payee.
    category_id : int, optional
        The default category for this payee.

    Returns
    -------
    None
    """
    logging.debug("inserting '{}' to Payee".format(name))
    payee = Payee(name=name,
                  display_name_id=display_name_id,
                  category_id=category_id)
    session.add(payee)


@utils.logged
def insert_transaction(insert_dict):
    """
    Insert a new transaction.

    Parameters
    ----------
    insert_dict : dict
        The transaction dictionary.

    Returns
    -------
    None
    """
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
    """
    Insert a new transaction_label.

    Parameters
    ----------
    value : str
        The string value for the transaction label.

    Returns
    -------
    None
    """
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


@utils.logged
def update_transaction(trans_id, update_dict):
    """
    Update a transaction with new values.

    Parameters
    ----------
    trans_id : int
        The ``id`` of the transaction to update.
    update_dict : dict
        The new values to use.

    Returns
    -------
    None
    """
    logging.info("Updating transaction")

    query = session.query(Transaction).filter_by(transaction_id=trans_id)
    query.update(update_dict)


# ---------------------------------------------------------------------------
### Other Functions
# ---------------------------------------------------------------------------
@utils.logged
def create_database():
    """
    Create the database.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
#    engine = sa.create_engine(engine_str, echo=False)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    return engine, session


@utils.logged
def copy_to_sa(engine, session, dump):
    """
    Copy...

    We know that our SQLite database will have the same structure as
    the SQLAlchemy ORM. So we just have to iterate through everything, copying
    data over.

    The engine and the session must already be created.

    Parameters
    ----------
    engine : :class:`SQLAlchemy.engine.Engine`
        The engine to work on.
    session : :class:`SQLAlchemy.orm.session.Session`
        The session to work on.
    dump : iterable
        A list or generator object that contains strings for table creation
        and data. Typically the result of :func:`sqlite_iterdump()` or
        ``sqlite3.iterdump()``.

    Returns
    -------
    None
    """
    logging.info('Starting copy to in-memory database')
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
    between columns while sqlite's ``iterdump()`` does not.

    .. warning::
       This function is specialized for PyBank and the single view that
       it contains. It will most likely not work for a generic database.

    .. note::
       The SQLAlchemy declaritive base class `Base` must be imported already.

    Parameters
    ----------
    engine : :class:`SQLAlchemy.engine.Engine`
        The engine to work on.
    session : :class:`SQLAlchemy.orm.session.Session`
        The session to work on.

    Returns
    -------
    sql : iterator
        The dump of the SQL.
    """
    logging.info("dumping database")
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
