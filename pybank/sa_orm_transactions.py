# -*- coding: utf-8 -*-
"""
Contains all of the transactions that act on the ORM.

Created on Sun Dec  6 20:58:58 2015

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
import sqlite3
import datetime
from decimal import Decimal

# Third Party
from sqlalchemy.schema import CreateTable
from sqlalchemy import text as saText

# Package / Application
try:
    # Imports used by unit test runners
    from . import sa_orm_base as base
    from . import utils
#    from . import (__project_name__,
#                   __version__,
#                   )
    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
        import sa_orm_base as base
        import utils
#        from __init__ import (__project_name__,
#                              __version__,
#                              )
        logging.debug("Imports for Spyder IDE")
    except ImportError:
        # Imports used by cx_freeze
        from pybank import sa_orm_base as base
        from pybank import utils
#        from pybank import (__project_name__,
#                            __version__,
#                            )
        logging.debug("imports for Executable")


# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
### Query Functions
# ---------------------------------------------------------------------------
def query_ledger_view():
    logging.debug("Quering Ledger View")
    return base.session.query(base.LedgerView).all()

# ---------------------------------------------------------------------------
### Insert Functions
# ---------------------------------------------------------------------------
def insert_account_group(name):
    logging.debug("inserting '{}' to AccountGroup".format(name))
    acct_group = base.AccountGroup(name=name)
    base.session.add(acct_group)


def insert_account(name, acct_num, user, institution_id, acct_group=None):
    logging.debug("inserting '{}' to Account".format(name))
    acct = base.Account(account_num=acct_num,
                        name=name,
                        user_name=user,
                        institution_id=institution_id,
                        account_group_id=acct_group)
    base.session.add(acct)


def insert_category(name, parent):
    logging.debug("inserting '{}' to Category".format(name))
    cat = base.Category(name=name, parent=parent)
    base.session.add(cat)


def insert_display_name(name):
    logging.debug("inserting '{}' to DisplayName".format(name))
    display_name = base.DisplayName(name=name)
    base.session.add(display_name)


def insert_institution(name, fid=None, org=None, url=None, broker=None):
    logging.debug("inserting '{}' to Institution".format(name))
    institution = base.Institution(name=name,
                                   fid=fid,
                                   org=org,
                                   url=url,
                                   broker=broker)
    base.session.add(institution)


def insert_memo(text):
    logging.debug("inserting '{}' to Memo".format(text))
    memo = base.Memo(text)
    base.session.add(memo)


def insert_payee(name, display_name_id=None, category_id=None):
    logging.debug("inserting '{}' to Payee".format(name))
    payee = base.Payee(name,
                       display_name_id=display_name_id,
                       category_id=category_id)
    base.session.add(payee)


def insert_transaction(account_id=None,
                       date=None,
                       enter_date=None,
                       check_num=None,
                       amount=None,
                       payee_id=None,
                       category_id=None,
                       transaction_label_id=None,
                       memo_id=None,
                       fitid=-1):
    logging.debug("inserting item to Transaction")

    date_fmt = '%Y-%m-%d'

    try:
        if date is None:
            date = datetime.datetime.today().date()
        else:
            date = datetime.datetime.strptime(date, date_fmt).date()
    except TypeError:
        raise

#    try:
#        if enter_date is None:
#            enter_date = datetime.datetime.today().date()
#        else:
#            enter_date = datetime.datetime.strptime(enter_date, date_fmt).date()
#    except TypeError:
#        raise

    trans = base.Transaction(account_id=account_id,
                             date=date,
                             enter_date=enter_date,
                             check_num=check_num,
                             amount=amount,
                             payee_id=payee_id,
                             category_id=category_id,
                             transaction_label_id=transaction_label_id,
                             memo_id=memo_id,
                             fitid=fitid)
    base.session.add(trans)


def insert_transaction_label(value):
    logging.debug("inserting '{}' to AccountGroup".format(value))
    trans_label = base.TransactionLabel(value=value)
    base.session.add(trans_label)


def insert_ledger(*args, **kwargs):
    """
    Handles inserting items into the ledger

    Every string needs to be matched to its ID in its table. If any new
    values are found, those need to 1st be added to the respective table.
    """
    pass


# ---------------------------------------------------------------------------
### Other Functions
# ---------------------------------------------------------------------------
utils.logged
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
    tables = base.Base.metadata.tables
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
        view = base.CreateView("ledger_view", base.LedgerView.selectable)
        yield str(view.compile(engine)) + ";COMMIT;"


def _test_iterdump_loop(dump_file):
    """
    Test the iterdump -> load -> iterdump loop.

    An iterdump file must already exist. sa_orm_base must be set up to
    be an in-memory database.
    """
    engine, session = base.create_database()

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

if __name__ == "__main__":
    pass
#    engine, session = base.create_database()

#    add_temp_item(session)
#    add_temp_item(session)
#    add_temp_item(session)

    # dump the database
#    dump = sqlite_iterdump(engine, session)
    # NOTE: *must* list() this generator or else, when copy_to_sa is called,
    #       the generator will act on the new engine and session, which has
    #       no data associated with it if they are closed or disposed.
#    dump = list(dump)

#    session.close()
#    engine.dispose()
#    input("waiting... (press enter)")

    # remove the database file
#    import os
#    os.remove("C:\\WinPython34\\projects\\github\\PyBank\\pybank\\_a.sqlite")

    # create a new database file
#    engine2, session2 = base.create_database()

    # copy over the existing data from the dump
#    copy_to_sa(engine2, session2, dump)

#    _test_iterdump_loop("C:\\WinPython34\\projects\\github\\PyBank\\pybank\\_generated_dump.txt")
#    _test_iterdump_loop("C:\\WinPython34\\projects\\github\\PyBank\\pybank\\_a.txt")
