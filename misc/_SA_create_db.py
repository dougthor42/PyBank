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
import logging
from decimal import Decimal as D

# Third Party
import sqlalchemy as sa
from sqlalchemy.ext import compiler as sa_compiler

# Package / Application
try:
    # Imports used by unit test runners
#    from . import utils
    from . import _SA_test
#    from . import (__project_name__,
#                   __version__,
#                   )
    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
#        import utils
        import _SA_test
#        from __init__ import (__project_name__,
#                              __version__,
#                              )
        logging.debug("Imports for Spyder IDE")
    except ImportError:
         # Imports used by cx_freeze
#        from pybank import utils
        from pybank import _SA_test
#        from pybank import (__project_name__,
#                            __version__,
#                            )
        logging.debug("imports for Executable")


# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
### Items needed to create a view in SQLAlchemy
# ---------------------------------------------------------------------------
class CreateView(sa.schema.DDLElement):
    def __init__(self, name, selectable):
        self.name = name
        self.selectable = selectable

class DropView(sa.schema.DDLElement):
    def __init__(self, name):
        self.name = name

@sa_compiler.compiles(CreateView)
def compile(element, compiler, **kw):
    sql_str = "CREATE VIEW {} AS {}"
    process_compiler = compiler.sql_compiler.process(element.selectable)
    return sql_str.format(element.name, process_compiler)

@sa_compiler.compiles(DropView)
def compile(element, compiler, if_exists=False, **kw):
#    sql_str = "DROP VIEW {}"
#    if if_exists:
    sql_str = "DROP VIEW IF EXISTS {}"
    return sql_str.format(element.name)

def view(name, metadata, selectable):
    t = sa.sql.table(name)

    for c in selectable.c:
        c._make_proxy(t)

    CreateView(name, selectable).execute_at('after-create', metadata)
    DropView(name).execute_at('before-drop', metadata)
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
            return None
        return D(value)

# ---------------------------------------------------------------------------
### Functions
# ---------------------------------------------------------------------------





#############################################################################
#############################################################################
#
# Now to do the same thing with the ORM...
#
#############################################################################
#############################################################################
print('\n\n=============== Start of ORM ===============')


# ---------------------------------------------------------------------------
### Classes
# ---------------------------------------------------------------------------

from sqlalchemy import event

# I don't really need events if I'm going with what I was doing earlier:
#   Decrypt the file to a temp one, do all actions on that, then periodically
#   re-encrypt with the new data.
def on_checkout(dbapi_conn, connection_rec, connection_proxy):
    print("handling on_checkout")

def on_connect(dbapi_conn, connection_record):
    print('handling on_connect')


engine = sa.create_engine('sqlite:///:memory:', echo=False)
event.listen(engine, 'checkout', on_checkout)
event.listen(engine, 'connect', on_connect)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

Base = declarative_base()

class Account(Base):
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

class AccountGroup(Base):
    __tablename__ = 'account_group'

    account_group_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)


class Category(Base):
    __tablename__ = 'category'

    category_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    parent = sa.Column(sa.Integer, sa.ForeignKey('category.category_id'))

    children = relationship("Category")


class DisplayName(Base):
    __tablename__ = 'display_name'

    display_name_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Integer)


class Institution(Base):
    __tablename__ = 'institution'

    institution_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    ofx_id = sa.Column(sa.Integer, sa.ForeignKey('ofx.ofx_id'))

    ofx = relationship('Ofx')


class Memo(Base):
    __tablename__ = 'memo'

    memo_id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.String)


class Ofx(Base):
    __tablename__ = 'ofx'

    ofx_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    ofx_org = sa.Column(sa.String)
    ofx_url = sa.Column(sa.String)


class Payee(Base):
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

class Transaction(Base):
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
    fit_id = sa.Column(sa.Integer)

    payee = relationship('Payee')
    category = relationship('Category')
    transaction_label = relationship('TransactionLabel')
    memo = relationship('Memo')


class TransactionLabel(Base):
    __tablename__ = 'transaction_label'

    transaction_label_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


def add_some_data(engine, session):
    # Add some dummy data
    import datetime
    date = datetime.date.today()
    trans = Transaction(transaction_id=1,
                        account_id=1,
                        date=date,
                        enter_date=date,
                        check_num=100,
                        amount=10.34,
                        payee_id=1,
                        category_id=1,
                        transaction_label_id=1,
                        memo_id=1,
                        fit_id=12345,
                        )

    display_name = DisplayName(display_name_id=1,
                               name='B',
                               )
    payee = Payee(payee_id=1,
                  name='aaa',
                  display_name_id=1,
                  category_id=1,
                  )
    trans_label = TransactionLabel(transaction_label_id=1,
                                   name='class-based label',
                                   )
    cat = Category(category_id=1,
                   name='category name',
                   parent=None,
                   )

    account = Account(account_id=1,
                      account_num='987654321',
                      name='Class-based',
                      institution_id=1,
                      user_name='SomeUser',
                      account_group_id=1,
                      )

    acct_group = AccountGroup(account_group_id=1,
                              name='Some group',
                              )


#    Session = sessionmaker(bind=engine)
#    session = Session()
    session.add_all([trans, display_name, payee, trans_label,
                     cat, account, acct_group])

    print("committing")
    session.commit()


#def print_some_data(session):
#    print('select')
#    result = engine.execute(sa.select([ledger_view])).fetchall()
#    print(result)




if __name__ == "__main__":

    # TODO: do I want outer joins?
    oj = sa.outerjoin(Transaction, Payee)
    oj = sa.outerjoin(oj, Category,
                      Category.category_id==Transaction.category_id)
    oj = sa.outerjoin(oj, TransactionLabel,
                      TransactionLabel.transaction_label_id==Transaction.transaction_label_id)
    oj = sa.outerjoin(oj, DisplayName,
                      DisplayName.display_name_id==Payee.display_name_id)
    oj = sa.outerjoin(oj, Account,
                      Account.account_id==Transaction.account_id)
    oj = sa.outerjoin(oj, Memo,
                      Memo.memo_id==Transaction.memo_id)

    func = sa.sql.func

    ledger_view = view('ledger_view', Base.metadata,
        sa.select([Transaction.date,
                   Transaction.account_id,
                   Account.name.label('AccountName'),
                   Transaction.enter_date,
                   Transaction.check_num,
                   func.coalesce(DisplayName.name,
                                 Payee.name).label('Payee'),
                   Payee.name.label('DownloadedPayee'),
                   TransactionLabel.name.label('TransactionLabel'),
                   Category.name.label('Category'),
                   Memo.text.label('Memo'),
                   Transaction.amount.label('Amount')]).\
        select_from(oj))

    print('drop if exists')
    engine.execute(sa.text("DROP VIEW IF EXISTS 'ledger_view'"))
    #metadata.create_all()


    #Session = sessionmaker(bind=engine)
    #session = Session()

    print('create all')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    # Add some dummy data
    add_some_data(engine, session)

    _SA_test.print_some_data(engine, session, [ledger_view])
