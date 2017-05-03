# -*- coding: utf-8 -*-
"""
Base for the SQLAlchemy Object Relational Mapper (ORM).

Contains all of the default table constructors used by PyBank.
"""
# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
import logging
import decimal
from decimal import Decimal
import warnings

# Third Party
import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.ext import compiler as sa_compiler
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

# Package / Application


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
    oj = sa.outerjoin(
        oj,
        Category,
        Category.category_id == Transaction.category_id,
    )
    oj = sa.outerjoin(
        oj,
        TransactionLabel,
        TransactionLabel.transaction_label_id == Transaction.transaction_label_id,
    )
    oj = sa.outerjoin(
        oj,
        DisplayName,
        DisplayName.display_name_id == Payee.display_name_id,
    )
    oj = sa.outerjoin(
        oj,
        Account,
        Account.account_id == Transaction.account_id,
    )
    oj = sa.outerjoin(
        oj,
        Memo,
        Memo.memo_id == Transaction.memo_id,
    )

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
    institution_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('institution.institution_id'),
    )
    account_group_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('account_group.account_group_id'),
    )

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
    transaction_label_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('transaction_label.transaction_label_id'),
    )
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


# ---------------------------------------------------------------------------
### Create the metadata and Session
# ---------------------------------------------------------------------------
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
