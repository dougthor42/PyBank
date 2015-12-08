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
#    from . import utils
#    from . import (__project_name__,
#                   __version__,
#                   )
    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
        import sa_orm_base as base
#        import utils
#        from __init__ import (__project_name__,
#                              __version__,
#                              )
        logging.debug("Imports for Spyder IDE")
    except ImportError:
        # Imports used by cx_freeze
        from pybank import sa_orm_base as base
#        from pybank import utils
#        from pybank import (__project_name__,
#                            __version__,
#                            )
        logging.debug("imports for Executable")


# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
### Functions
# ---------------------------------------------------------------------------


def add_temp_item(session):
    temp_memo = base.Memo(text="this is a memo")
    session.add(temp_memo)
    print(session.new)
    session.commit()


def query_all(table):
    print("querying table!")
    return


def query_view():
    return base.session.query(base.LedgerView).all()


def read_ledger(session):
    return list(session.query(base.Memo).order_by(base.Memo.memo_id))


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
