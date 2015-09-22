# -*- coding: utf-8 -*-
"""
Demo of using SQLAlchemy to create the PyBank database.

Created on Mon Sep 21 15:31:10 2015

Usage:
    _SA_create_db.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""

# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
#import sqlite3
import logging

# Third Party
import sqlalchemy as sa
#from sqlalchemy_views import CreateView, DropView


# Package / Application
try:
    # Imports used for unittests
#    from . import utils
#    from . import (__project_name__,
#                   __version__,
#                   )
    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
#        import utils
#        from __init__ import (__project_name__,
#                              __version__,
#                              )
        logging.debug("Imports for Spyder IDE")
    except ImportError:
         # Imports used by cx_freeze
#        from pybank import utils
#        from pybank import (__project_name__,
#                            __version__,
#                            )
        logging.debug("imports for Executable")


# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
### Classes
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
### Functions
# ---------------------------------------------------------------------------


engine = sa.create_engine("sqlite:///:memory:", echo=False)
#engine = sa.create_engine("sqlite:///_slqalchemy_db.db", echo=True)

metadata = sa.MetaData(engine)

acct = sa.Table('acct', metadata,
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('acct_num', sa.String, nullable=False),
                sa.Column('name', sa.String, nullable=False),
                sa.Column('institution_id', None, sa.ForeignKey('institution.id')),
                sa.Column('user_name', sa.String, nullable=False),
                sa.Column('group', sa.Integer),     # TODO: create group tbl
                )


category = sa.Table('category', metadata,
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('name', sa.String, nullable=True),
                    sa.Column('parent', None, sa.ForeignKey('category.id')),
                    )

display_name = sa.Table('display_name', metadata,
                        sa.Column('id', sa.Integer, primary_key=True),
                        sa.Column('display_name', sa.String, nullable=False),
                        )

# TODO: split out ofx data to separate table
institution = sa.Table('institution', metadata,
                       sa.Column('id', sa.Integer, primary_key=True),
                       sa.Column('name', sa.String, nullable=False, unique=True),
                       sa.Column('ofx_id', sa.Integer, nullable=False),
                       sa.Column('ofx_org', sa.String, nullable=False),
                       sa.Column('ofx_url', sa.String, nullable=False),
                       )

label = sa.Table('label', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('name', sa.String, nullable=False),
                 )

payee = sa.Table('payee', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('name', sa.String, nullable=False, unique=True),
                 sa.Column('display_name_id', None, sa.ForeignKey('display_name.id')),
                 sa.Column('category_id', None, sa.ForeignKey('category.id')),
                 )

transaction = sa.Table('transaction', metadata,
                       sa.Column('id', sa.Integer, primary_key=True),
                       sa.Column('date', sa.Date, nullable=False),  # datetime?
                       sa.Column('enter_date', sa.Date),            # datetime?
                       sa.Column('check_num', sa.Integer),
                       sa.Column('amount', sa.Numeric),
                       sa.Column('payee_id', None, sa.ForeignKey('payee.id')),
                       sa.Column('category_id', None, sa.ForeignKey('category.id')),
                       sa.Column('label_id', None, sa.ForeignKey('label.id')),
                       sa.Column('memo', sa.String),
                       sa.Column('fitid', sa.Integer),
                       )

#metadata.create_all(engine)

# Create our main View (though it's currently acting like a standard table):
from sqlalchemy.schema import DDLElement
from sqlalchemy.sql import table
from sqlalchemy.ext import compiler

class CreateView(DDLElement):
    def __init__(self, name, selectable):
        self.name = name
        self.selectable = selectable

class DropView(DDLElement):
    def __init__(self, name):
        self.name = name

@compiler.compiles(CreateView)
def compile(element, compiler, **kw):
    return "CREATE VIEW %s AS %s" % (element.name, compiler.sql_compiler.process(element.selectable))

@compiler.compiles(DropView)
def compile(element, compiler, **kw):
    return "DROP VIEW %s" % (element.name)

def view(name, metadata, selectable):
    t = table(name)

    for c in selectable.c:
        c._make_proxy(t)

    CreateView(name, selectable).execute_at('after-create', metadata)
    DropView(name).execute_at('before-drop', metadata)
    return t





oj = sa.outerjoin(transaction, payee)
oj = sa.outerjoin(oj, category, category.c.id==transaction.c.category_id)
oj = sa.outerjoin(oj, label)
oj = sa.outerjoin(oj, display_name, display_name.c.id==payee.c.display_name_id)

func = sa.sql.func

ledger_view = view('ledger_view', metadata,
                   sa.select([transaction.c.date.label('date'),
                              transaction.c.enter_date.label('enter_date'),
                              transaction.c.check_num.label('check_num'),
                              func.coalesce(display_name.c.display_name,
                                            payee.c.name).label('payee'),
                              payee.c.name.label('downloaded_payee'),
                              label.c.name.label('label'),
                              category.c.name.label('category'),
                              transaction.c.memo.label('memo'),
                              transaction.c.amount.label('amount')]).\
                   select_from(oj))


metadata.create_all()


# Add some dummy data
import datetime
date = datetime.date.today()
transaction.insert().execute(id=1, date=date, enter_date=date,
                             check_num=100, amount=10.34, payee_id=1,
                             category_id=1, label_id=1, memo="memo", fitid=10)

display_name.insert().execute(id=1, display_name="B")
payee.insert().execute(id=1, name='aaa', display_name_id=1, category_id=1)
label.insert().execute(id=1, name='some label')
category.insert().execute(id=1, name='category_name', parent=None)


result = engine.execute(sa.select([ledger_view])).fetchall()
print(result)
