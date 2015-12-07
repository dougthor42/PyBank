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

# Third Party
from sqlalchemy.schema import CreateTable, Table
from sqlalchemy import select, sql

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


def read_ledger(session):
    return list(session.query(base.Memo).order_by(base.Memo.memo_id))


def copy_to_sa():
    """
    We know that our SQLite database will have the same structure as
    the SQLAlchemy ORM. So we just have to iterate through everything, copying
    data over.
    """


def copy_from_sa(engine, session):
    """
    Copy from SQLAlchemy to an SQLite in-memory database so that I can
    iterdump that and encrypt the results
    """
    # 1st create the database and a cursor
#    conn = sqlite3.connect(":memory:")
    conn = sqlite3.connect("C:\\WinPython34\\projects\\github\\PyBank\\pybank\\_a.db")
    cursor = conn.cursor()

    # Then copy over the tables and data
    tables = base.Base.metadata.tables

    for name, table in tables.items():
        print("getting sql for {}".format(name))
        cursor.execute(str(CreateTable(table).compile(engine)))
        data = session.query(table).all()
        for row in data:
            cursor.execute("""INSERT INTO "{}" VALUES{}""".format(name, row))

    # We know there is 1 view, so add that too
    view = base.CreateView("ledger_view", base.LedgerView.selectable)   # hack

    cursor.execute(str(view.compile(engine)))

    # Commit the table/view creation transactions
    conn.commit()

if __name__ == "__main__":
    engine, session = base.create_database()

    add_temp_item(session)
    add_temp_item(session)
    add_temp_item(session)

    copy_from_sa(engine, session)
