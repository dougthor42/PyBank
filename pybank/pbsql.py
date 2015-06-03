# -*- coding: utf-8 -*-
"""
Handles SQLite transactions for PyBank.

Created on Tue May 12 13:23:30 2015

Usage:
    sqlite.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""

# Standard Library
import sys
import shutil
import sqlite3
import logging
import abc
import os.path as osp
from contextlib import closing

# Third-Party
from docopt import docopt

# Package / Application
if __name__ == "__main__":
    sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
#from __init__ import VERSION


DATABASE = "test_database.db"

def docstring():
    """
Details:
--------

See: https://crackstation.net/hashing-security.htm


TABLES
======
The database consists of the following tables:


acct:
------
contains information on the accounts.

id : uint16, primary key
    A unique identifier for the table
acct_num : string
    The account number
name : string
    The account name
institution_id : uint16
    institution ID
username : string
    The user's login information
acct_group : int
    The acct_group ID that this account belongs to.


institution:
-------------
Contains connection info on the institutions

id : uint16, primary key
    Unique identifier for the institution
name : string
    Name of the institution
ofx_id : int
    Financial Institution's ofx ID
ofx_org : string
    Financial Institution's ofx ORG
ofx_url : string (url)
    Financial institution's ofx url


transaction_0:
----------
Individual tables for each account ID. This is the core where all of
the transactions are held. multiple tables: transactions_1, transactions_2,
transactions_3, etc. one for each item in accts.

names will be acct_1, acct_2, acct_37, acct_567, etc.

id : utint32, primary key
    Unique identifier for the transaction
date : date
    Date (and time?) that the transaction happened, from <DTPOSTED>
enter_date : date
    Date (and time?) that the transaction was entered
trans_type : string
    Transaction type, taken from the <TRNTYPE> tag in the ofx file.
check_num : uint32
    Check number, taken from <CHECKNUM>
amount : string (decimal.Decimal?)
    The transaction amount. Converted to decimal.Decimal when processing.
    Taken from <TRNAMT>
payee_id : uint32
    the payee key, linked with <NAME> and the payee table
category_id : uint16
    A category specifier
label_id : uint16, optional
    the label key
memo : string
    The memo line from <MEMO>
fitid : uint32 (or string?)
    The order in which the transaction took place, from <FITID>. It appears
    that <FITID> is the date string followed by a number::

        <FITID>201505082        # 2015-05-08 (Friday), 2nd transaction
        ...
        <FITID>201505081        # 2015-05-08 (Friday), 1st transaction


category:
-----------
Category IDs and Names.

This table apparently follows the Adjacency List Model. See
http://mikehillyer.com/articles/managing-hierarchical-data-in-mysql/

id : uint16, primary key
    Unique identifier for the category
name : string
    string name for the category
parent : uint16
    the Category parent ID. For example, Car Insurance would would be
    5, if the Car category is 5.


label:
-------
Label IDs and names. Labels are used to group multiple different
transactions into a one unit - for example, grouping all transactions
from a vacation.

id : uint16, primary key
    Unique identifier for the label
name : string
    Label name


payee:
-------
Contains all of the payee names and default categories
# TODO: Should name be a primary key as well?

id : uint32, primary key
    Unique identifier for the payee
name : string
    downloaded name of the payee
display_name_id : int, optional
    If present, display this name instead of the normal one (renaming rules)
category : uint16
    default category that this payee should be sorted into.


renaming_rule:
-------------
Contains naming rules for renaming payees
# TODO: Figure out how I want to implement this.
I think I need to look up foreign keys and many-to-one relationships.

id : uint32, primary key        # XXX: Is this needed?
    Unique identifier for the renaming rule
old_name : string
    the old name
new_name : string
    What the new name should be


display_name:
-------------
Contains the display names for various items.

id : int, primary key
    Unique identifier for the display name
name : string
    The name to display


VIEWS:
======

v_ledger_0:
----------
Joins everything together, yay!

"""
    pass


# TODO: SQLite Adaptos and Converters
# https://docs.python.org/3.4/library/sqlite3.html#sqlite-and-python-types

def validate_db():
    """
    Validate the database file, making sure it has all the correct tables
    and whatnot.
    """
    pass


# TODO: Refactor for better unittests
def create_trans_tbl(database, acct_id):
    """
    Creates a transaction table for the given acct_id.

    Table name follows this format: transaction_<acct_id> and so would look
    like:

    `>>> create_trans_tbl(12):
    transaction_12

    # TODO: zero padding yes or no?
    #       transaction_01
    #       transaction_1

    Parameters:
    -----------
    database : string
        File path of the SQLite database to modify.

    acct_id : int
        The account ID that these transactions should be linked to

    Returns:
    --------
    tbl_name : string
        The created table's name.

    """
    # TODO: execute from file instead?
    # TODO: make this function return just a creation string?
    tbl_name = "transaction_{}".format(acct_id)
    transaction = """
        CREATE TABLE `{}` (
        `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        `date` TEXT NOT NULL,
        `enter_date` TEXT,
        `check_num` INTEGER,
        `amount` TEXT NOT NULL,
        `payee_id` INTEGER,
        `category_id` INTEGER,
        `label_id` INTEGER,
        `memo` TEXT,
        `fitid` TEXT
        );""".format(tbl_name)

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute(transaction)
    conn.commit()
    cursor.close()
    conn.close()
    return tbl_name


# TODO: Refactor for better unittests
def create_ledger_view(database, acct_id):
    """
    Creates a ledger view for the given acct_id.

    View name follows this format: v_ledger_<acct_id> and so would look
    like:

    `>>> create_ledger_view(15)
    v_ledger_15

    Parameters:
    -----------
    database : string
        File path of the SQLite database to modify.

    acct_id : int
        The account ID that the view should be linked to

    Returns:
    --------
    view_name : string
        The created view's name.

    """
    # TODO: execute from file instead?
    # TODO: make this function return just a creation string?
    view_name = "v_ledger_{}".format(acct_id)
    view = """
        CREATE VIEW {v_name} AS
            SELECT
                trans.date,
                trans.enter_date,
                trans.check_num,
                COALESCE(display_name.display_name, payee.name) as "payee",
                payee.name as "downloaded_payee",
                label.name AS "label",
                category.name AS "category", -- # TODO: Python Maps this instead?
                trans.memo,
                trans.amount
            FROM
                transaction_{acct} AS trans
                LEFT OUTER JOIN payee
                    ON trans.payee_id = payee.id
                LEFT OUTER JOIN category
                    ON trans.category_id = category.id
                LEFT OUTER JOIN label
                    ON trans.label_id = label.id
                LEFT OUTER JOIN display_name
                    ON payee.display_name_id = display_name.id
          """.format(v_name=view_name, acct=acct_id)

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    # can't execute multiple statements, so I bought this out.
    cursor.execute("DROP VIEW IF EXISTS {v_name}".format(v_name=view_name))
    conn.commit()
    cursor.execute(view)
    conn.commit()
    cursor.close()
    conn.close()
    return view_name

def copy_blank_db(filename=DATABASE):
    """
    Copies the blank database to the working directory.

    Parameters:
    -----------
    filename : string, optional
        The filename to save the working database as

    Returns:
    --------
    None

    """
#    logging.debug("debugging")
#    logging.info("Info!")
#    logging.warn("warn: you should do this instead")
#    logging.warning("warning: you can't do anything about this")
#    logging.error("error")
#    logging.critical("critical")
    logging.info("Copying blank database to working dir")
    try:
        # copy the blank database file
        shutil.copy2("..\\blank_database.db", ".\\{}".format(filename))
    except FileNotFoundError:
        # create the DB file instead
        logging.warning("Blank database not found; creating from scratch.")
        create_db(filename)


# TODO: Refactor for better unittests
def create_db(filename=DATABASE):
    """
    Creates the SQLite database file.

    Copies the blank database to the working directory or, if the blank
    database is not found for some reason, creates it directly.

    Parameters:
    -----------
    filename : string, optional
        The filename to save the database as. Defaults to DATABASE.

    Returns:
    --------
    None

    """
    logging.info("Creating empty database")
    acct = """
        CREATE TABLE `acct` (
        `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        `acct_num` TEXT NOT NULL,
        `name` TEXT NOT NULL,
        `institution_id` INTEGER NOT NULL,
        `username` TEXT NOT NULL,
        `group` INTEGER
        );"""

    category = """
        CREATE TABLE `category` (
        `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        `name` TEXT NOT NULL,
        `parent` INTEGER
        );"""

    institution = """
        CREATE TABLE `institution` (
        `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        `name` TEXT NOT NULL,
        `ofx_id` INTEGER NOT NULL,
        `ofx_org` TEXT NOT NULL,
        `ofx_url` TEXT NOT NULL
        );"""

    label = """
        CREATE TABLE `label` (
        `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        `name` TEXT NOT NULL
        );"""

    payee = """
        CREATE TABLE `payee` (
        `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        `name` TEXT NOT NULL,
        `display_name_id` INTEGER,
        `category_id` INTEGER
        );"""

    display_name = """
        CREATE TABLE `display_name` (
        `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        `display_name` TEXT NOT NULL
        );"""

    tables = [acct, category, institution, label, payee, display_name,
              ]

    try:
        conn = sqlite3.connect(filename)

        cursor = conn.cursor()

        for tbl in tables:
            cursor.execute(tbl)

        conn.commit()
    except sqlite3.OperationalError:
        logging.exception("SQL Error during database creation")
    else:
        # runs if no error
        cursor.close()
        conn.close()
    finally:
        # runs if there's an error, then error re-raised after this
        pass

    create_trans_tbl(filename, 0)
    create_ledger_view(filename, 0)

### #------------------------------------------------------------------------
### Core Database Functions
### #------------------------------------------------------------------------

# TODO: Can I separate the sqlite3.connect command into a different function?
# TODO: Refactor for better unittests
def db_execute(database, cmd, *args):
    """
    Executes a database command.

    Uses context managers to handle connections and cursors. Logs the
    action to DEBUG.

    Parameters:
    -----------
    database : string
        The filepath of the SQLite database to connect to

    cmd : string
        The SQLite command to execute.

    Returns:
    --------
    None

    """
    # TODO: different context manager for connection? - auto-commit / rollback
    #https://docs.python.org/3.4/library/sqlite3.html#using-sqlite3-efficiently
    logcmd = cmd.replace("?", "{}").format(*args)
    logstr = "db_execute: {db} || {sqlstr}"
    logging.debug(logstr.format(db=database, sqlstr=logcmd))
    with closing(sqlite3.connect(database)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(cmd, args)
            conn.commit()
    return None


# TODO: Refactor for better unittests
def db_insert(database, cmd, *args):
    """
    Executes a database insert and returns the inserted row id.

    Uses context managers to handle connections and cursors. Logs the action
    to DEBUG.

    Parameters:
    -----------
    database : string
        The filepath of the SQLite database to connect to

    cmd : string
        The SQLite command to execute.

    Returns:
    --------
    id : int
        The id of the inserted item.
    """
    # TODO: different context manager for connection? - auto-commit / rollback
    #https://docs.python.org/3.4/library/sqlite3.html#using-sqlite3-efficiently
    logcmd = cmd.replace("?", "{}").format(*args)
    logstr = "db_insert: {db} || {sqlstr}"
    logging.debug(logstr.format(db=database, sqlstr=logcmd))
    # TODO: experiement with context managers
    #       Specifically, see if having the `return` inside the context
    #       manager is any different from having it outside. I'm interested
    #       in *when* __exit__() is called: if return is a function, such
    #       as return another_function(data), does the contect manager
    #       wrap that one too (is __exit__() called before or after
    #       another_function() completes?)?
    with closing(sqlite3.connect(database)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(cmd, args)
            conn.commit()
            last_row_id = cursor.lastrowid
#            return cursor.lastrowid
    return last_row_id


# TODO: Refactor for better unittests
def db_query(database, query, *args):
    """
    Execute a database query.

    Uses context manager to handle connections and cursors. Logs the action
    to DEBUG.

    Parameters:
    -----------
    database : string
        The filepath of the SQLite database to connect to

    query : string
        The SQLite query to execute.

    Returns:
    --------
    retval : dict or list of dicts
        The results of the database query

    """
    # TODO: different context manager for connection? - auto-commit / rollback
    #https://docs.python.org/3.4/library/sqlite3.html#using-sqlite3-efficiently
    # TODO: Look into sqlite3.row_factory
    logquery = query.replace("?", "{}").format(*args)
    logstr = "db_query: {db} || {sqlstr}"
    logging.debug(logstr.format(db=database, sqlstr=logquery))
    with closing(sqlite3.connect(database)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(query, args)
            #conn.commit()       # not needed because it's a query
            retval = cursor.fetchall()
    return retval


class SQLTable(abc.ABC):
    """
    Class containing all table accessors.

    In theory.
    """
    def __init__(self, database, table):
        self.database = database
        self.table = table

    def add(self, column_data):
        """
        Adds a single item to the current data table.

        Parameters:
        -----------
        column_data : dict
            A dictionary of column-value pairs to add.

        Returns:
        --------
        db_insert.retval : int
            The primary key of the last inserted item.

        Notes:
        ------
        # TODO: Decide if I want to input a dict of column-value pairs, or
        if I want to input a **kwargs where the named arg is the
        column and the value is the column value.

        Bascially, it's this::

            SQLTable.add({'column1':1, 'column2'='value2', ... })

        versus this::

            SQLTable.add(column1=1, column2='value2)

        I think it will be easier if I just pass a dict rather than doing
        parameter unpacking (2nd option).
        """
        columns = []
        values = []

        for key, value in column_data.items():
            columns.append(_sql_param(key))
            values.append(value)

        placeholders = ", ".join(['?'] * len(column_data))
        columns = ", ".join(columns)

        cmd = """
            INSERT INTO `{tbl}`({cols})
            VALUES ({vals})"""
        cmd = cmd.format(tbl=self.table, cols=columns, vals=placeholders)
        return db_insert(self.database, cmd, *values)

    def delete(self, pk):
        """
        Deletes a single item from the current table.

        Parameters:
        -----------
        pk : int
            The primary key (id) to delete.

        Returns:
        --------
        None
        """
        cmd = "DELETE FROM {tbl} WHERE id=?".format(tbl=self.table)
        return db_execute(self.database, cmd, pk)

    def read(self, pk):
        """
        Reads a row from the current table.

        Parameters:
        -----------
        pk : int
            The primary key of the current table.

        Returns:
        --------
        db_read.retval : list of tuples or list of dicts.
            The values read from the database.


        Notes:
        ------

        TODO:
        ~~~~~
        Decide if I want to return a list of tuples (current method)
        or if I want to return a list of dicts (proposed).
        """
        query = """SELECT * FROM `{}` WHERE `id`=?""".format(self.table)
        return db_query(self.database, query, pk)

    def read_all(self):
        """
        Reads the entire current table.

        Parameters:
        -----------
        None

        Returns:
        --------
        List of tuples or list of dict containing the entire table's data.
        """
        query = "SELECT * FROM `{}`".format(self.table)
        return db_query(self.database, query)

    @abc.abstractmethod
    def update(self, pk, *args):
        """
        """
        pass


class SQLView(abc.ABC):
    """
    Parent class for all views
    """
    def __init__(self, database, view):
        self.database = database
        self.view = view

    def read(self):
        """
        """
        pass

    def read_all(self):
        """
        """
        query = "SELECT * FROM `{}`".format(self.view)
        return db_query(self.database, query)


# XXX: Do I want to have subclasses for each table type?
class AcctTable(SQLTable):
    """
    """
    def __init__(self):
        pass

    # TODO: Gotta be a better way to do these add, read, read_all, delete, etc.
    def add(column_data):
        """ Adds an account """
        return super().add(column_data)

    def update(self):
        """
        """
        pass


class TransactionTable(SQLTable):
    """
    Child class of ``SQLTable``.

    Contains transaction information.
    """
    def __init__(self):
        pass

    def add(self, column_data):
        """
        Adds a transaction.
        """
        # TODO: add error raising for values that can't be null.
        #       Or should I catch error after the fact?
        return super().add(column_data)

    # TODO: Figure out how I want to handle the args of this function.
    #       User will be updating with the UI, so I might be able to just
    #       overwrite everything, because the UI should have the prevvious values
    #       already.
    def update(acct_id, trans_id, **kwargs):
        """
        Updates a transaction.

        Parameters:
        -----------
        acct_id : int
            The account ID that the transaction belongs to.
        trans_id : int
            The transcation ID to update
        kwargs :
            The items to update.

        Returns:
        --------
        None
        """
        cmd = """
            UPDATE `transaction_{}'
            SET xxx
            WHERE id=?
            """
        return db_execute(DATABASE, cmd, acct_id)


class InstitutionTable(SQLTable):
    """
    Child class of ``SQLTable``.

    Contains all of the used institution information.
    """
    def update(self):
        pass

class CategoryTable(SQLTable):
    """
    Child class of ``SQLTable``.

    Contains all of the known categories and their relationships.
    """
    # TODO: category hierarchy or something like that.
    def update(self):
        pass

    def make_tree(self):
        pass


class LabelTable(SQLTable):
    """
    Child class of ``SQLTable``.

    Contains all of the known labels.
    """
    def update(self):
        pass


class PayeeTable(SQLTable):
    """
    Child class of ``SQLTable``.

    Contains all of the known payees and their default category.

    TODO: Add column to this table for renaming.
        display_name_id : int, optional
            the link to the renaming table.

    Notes:
    ------
    I don't have most of the default methods (add, delete, etc.) because they
    are taken care of by the parent class.

    Although, I could add them and use super() because 'explicit is better
    than implict'... but that's much more work i think. And if I change the
    signature in the parent I have to do it everywhere else.
    """
#    def __init__(self):
#        pass

#    def add():
#        pass

#    def delete(self):
#        pass

#    def read(self):
#        pass

#    def read_all(self):
#        pass

    def update(self):
        pass


class DisplayNameTable(SQLTable):
    """
    Child class of ``SQLTable``.

    Contains all of the display names (renaming rules for payess, etc.).
    """
    def update(self):
        pass


class LedgerView(SQLView):
    """
    Child class of ``SQLView``.

    Contains all of the items displayed in the ledger.
    """
    pass


def generate_category_strings(cat_list,
                              parent_item=None,
                              sent_str=None,
                              retval=[],
                              ):
    """
    Concatenates categories together and returns a list of them.

    Parameters:
    -----------
    cat_list : list of (id, name, parent) tuples
        The data to create strings from. This must be a list (or list-like)
        of (id, name, parent_id) tuples (or list-like).

    parent_item :
        Only used during recursion.

    sent_str :
        Only used during recursion

    retlist :
        Only used during recursion.

    Returns:
    --------
    retlist : list of strings
        A list of dot-notation strings.

    Examples:
    ---------

    >>> data = [(1, "A", 0), (2, "B", 1), (3, "C", 1), (4, "D", 2),
    ...         (5, "E", 2), (6, "F", 3), (7, "G", 2), (8, "H", 6),
    ...         ]
    >>> generate_category_strings(data)
    ['A', 'A.B', 'A.B.D', 'A.B.E', 'A.B.G', 'A.C', 'A.C.F', 'A.C.F.H']

    """
    if parent_item is None:
        parent_item = cat_list[0]
        retval.append(parent_item[1])

    parent_id = parent_item[0]
    parent_name = parent_item[1]

    if sent_str is None:
        sent_str = parent_name

    # Find the children
    children = [_x for _x in cat_list if _x[2] == parent_id]

    if len(children) == 0:
        # base case (no children), so we return the full path
        return ["{}.{}".format(sent_str, parent_name)]
    else:
        # children exist so we need to iterate through them.
        for child in children:
            # create an incomplete path string and add it to our return value
            str_to_send = "{}.{}".format(sent_str, child[1])
            retval.append(str_to_send)
            # recurse using the current child as the new parent
            generate_category_strings(cat_list, child, str_to_send, retval)
        return retval


### #------------------------------------------------------------------------
### Other
### #------------------------------------------------------------------------

def update_db():
    """
    Updates the database with the new entries.
    """
    pass


def insert_item():
    """
    Inserts an item to the database.
    """
    pass


def update_item():
    """
    Updates an item in the database with new values.
    """
    pass


def append_item():
    """
    Adds a new item to the end of the database
    """
    pass


def _sql_param(item):
    """
    Formats an item as a SQLite parameter by surrounding it in backticks
    """
    return "`{}`".format(item)


def main():
    """
    Runs when module is called directly.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    RuntimeError
    """
    docopt(__doc__, version="0.0.1")    # TODO: pull VERSION from __init__
    raise RuntimeError("This module is not meant to be run by itself")


if __name__ == "__main__":
#    copy_blank_db()
#    payee = PayeeTable(DATABASE, 'payee')
#    a = payee.add({'name':"dfsf", 'category_id':5})
#    b = payee.read(a)
#    print(b)
#    query_str = """
#        SELECT * FROM category
#        """
#
#    result = db_query(DATABASE, query_str)
#
#    a = generate_category_strings(result)
#    for item in sorted(a):
#        print(item)
    pass
