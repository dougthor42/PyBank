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


# TODO: SQLite Adaptors and Converters
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


def db_query_single(database, query, *args):
    """
    Queries a single item from the database
    """
    logquery = query.replace("?", "{}").format(*args)
    logstr = "db_query_single: {db} || {sqlstr}"
    logging.debug(logstr.format(db=database, sqlstr=logquery))
    with closing(sqlite3.connect(database)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(query, args)
            #conn.commit()       # not needed because it's a query
            retval = cursor.fetchone()
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

    def row_count(self):
        """ Returns the number of rows in the table or view """
        query = "SELECT COUNT(*) FROM `{}`".format(self.table)
        return db_query(self.database, query)[0]


class SQLView(abc.ABC):
    """
    Parent class for all views.

    Child class must define ``self.view``.
    """
    def __init__(self, database, acct_id):
        self.database = database
        self.acct_id = acct_id

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
    def __init__(self, database, acct_id):
        super().__init__(database, acct_id)
        self.view = "v_ledger_{}".format(self.acct_id)
        self.trans_tbl = "transaction_{}".format(self.acct_id)

    def insert_row(self):
        """
        Adds a new blank row to the ledger.
        """
        sql = "INSERT INTO `{}` DEFAULT VALUES".format(self.trans_tbl)
        new_row = db_insert(self.database, sql)
        return new_row

    def update_transaction(self, row, col, value):
        if col == 1:
            self._update_date(row, value)
        elif col == 2:
            self._update_date_entered(row, value)
        elif col == 3:
            self._update_checknum(row, value)
        elif col == 4:
            self._update_payee(row, value)
        elif col == 5:
            self._update_downloaded_payee(row, value)
        elif col == 6:
            self._update_memo(row, value)
        elif col == 7:
            self._update_category(row, value)
        elif col == 8:
            self._update_label(row, value)
        elif col == 9:
            self._update_amount(row, value)
        else:
            # Can't raise IndexError because that results in infinite loop
            # from gui.LedgerGridBaseTable._set_value()
            raise Exception("Invalid column: {}".format(col))

    def _update_date(self, row, value):
        print("Updating date")
        pass

    def _update_date_entered(self, row, value):
        print("Updating date_entered")
        pass

    def _update_checknum(self, row, value):
        """
        Updates the Checknum for a given row.

        Parameters:
        -----------
        row : int
            the row to update

        value : int
            The new check number

        Returns:
        --------
        None

        """
#        print("Updating check_num")
        sql = "UPDATE `{tbl}` SET `{col}`=? WHERE id={row}"
        col_name = "check_num"
        sql = sql.format(tbl=self.trans_tbl, col=col_name, row=row)
        try:
            int(value)
        except TypeError:
            err = "Checknum must be castable to int. Got '{}'".format(value)
            raise TypeError(err)
        else:
            # runs if no error
            db_execute(self.database, sql, value)

    def _update_payee(self, row, value):
        print("Updating payee")
        # first, check for the new value in the database
        sql = "SELECT * FROM `payee` WHERE name=?"
        result = db_query(self.database, sql, value)
        if result == []:
            print("payee not found, adding")
            sql = "INSERT INTO `payee`(name) VALUES (?)"
            new_id = db_insert(self.database, sql, value)
            # TODO: I can get rid of a db query by using new_id directly.
            self._update_payee(row, value)
        elif len(result) > 1:
            err = "Duplicate payee name `{}` found! How'd we get here?".format(value)
            raise Exception(err)
        else:
            print("Payee found, using payee.id")
            sql = "UPDATE `{tbl}` SET `{col}`=? WHERE id={row}"
            col_name = "payee_id"
            sql = sql.format(tbl=self.trans_tbl, col=col_name, row=row)
            db_execute(self.database, sql, result[0][0])

    def _update_downloaded_payee(self, row, value):
        print("downloaded_payee is read-only")
        pass

    def _update_label(self, row, value):
        print("Updating label")
        pass

    def _update_category(self, row, value):
        print("Updating category")
        pass

    def _update_memo(self, row, value):
        """ Updates the memo field """
        if value == '':
            value = None
#        print("Updating memo with new value: `{}`".format(value))
        sql = "UPDATE `{tbl}` SET `{col}`=? WHERE id={row}"
        col_name = "memo"
        sql = sql.format(tbl=self.trans_tbl, col=col_name, row=row)
        db_execute(self.database, sql, value)

    def _update_amount(self, row, value):
        sql = "UPDATE `{tbl}` SET `{col}`=? WHERE id={row}"
        col_name = "amount"
        sql = sql.format(tbl=self.trans_tbl, col=col_name, row=row)
        try:
            float(value)
#            print("Updating amount with new value: `{}`".format(value))
        except ValueError:
            raise ValueError("`Amount` must be a number")
        else:
            db_execute(self.database, sql, value)


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

# TODO: rename
def find_if_payee_already_in_payee_table(payee):
    """
    searches for the payee in the payee table.

    Adds payee to table if it doesn't exist
    """
    pass

#def update_ledger_transaction():
#    """
#    Updates a transaction in the transaction table.
#
#    Parameters:
#    -----------
#    database : string
#        The SQLite database file that we're working on
#
#    trans_table : string
#        The table name that we're going to update a transaction in.
#
#    Returns:
#    --------
#    ???
#
#    Notes:
#    ------
#    This is a pretty complicated function.
#
#    When updating a tranaction value, we need to do different things based
#    on the column that we're in:
#
#    date:
#        validate the new value as a date, convert to string,
#        and then write to database
#    enter_date:
#        same as date
#    check_num:
#        validate the new value as int, validate that it's not a
#        duplicate check number (warn?), and write to database
#    payee:
#        This is a merge of the payee and display_name table, so some fancy
#        stuff needs to be done.
#    downloaded_payee:
#        This is from the payee_id column. When user enters value here, I need
#        to first check if it's in the payee table. If so, then get the
#        payee.id and write that to transaction_0.payee_id. If not, then
#        enter a new item into the payee table and write that to the
#        transaction table
#        # TODO: how do I handle this? User modifies Payee or Downloaded_Payee?
#    label:
#        User selects from dropdown, write int value to DB. If user writes in
#        new value, then add to label table and enter new id to transaction_0.
#    category:
#        User selects from dropdown, write int value to DB. For now, no option
#        to add new category.
#        # TODO: Add ability to make new category.
#    memo:
#        Write string to DB.
#    amount:
#        validate the new value is float, convert to decimal.Decimal,
#        convert to string, write to database.
#        Also update the balance column?
#    """
#    pass


def update_date_field():
    """
    Takes the string that the user enters and validates it as a datetime.
    """
    pass


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


def insert_row():
    """
    Inserts a blank row (no data) to the database.
    """
    pass

# XXX: quick proof-of-concept hack
def insert_ledger_row(database=DATABASE, ledger="transaction_0"):
    sql = "INSERT INTO `{}` DEFAULT VALUES".format(ledger)
    db_insert(database, sql)

def update_item():
    """
    Updates an item in the database with new values.
    """
    pass

# XXX: quick proof-of-concept hack
def update_ledger_item(row, column,
                       database=DATABASE, ledger="transaction_0",
                       ):
    """
    Updates a ledger item.
    """
    col_names = [
                 "date",
                 "enter_date",
                 "check_num",
                 "payee",
                 "downloaded_payee",
                 "label",
                 "category",
                 "memo",
                 "amount",
                 ]

    cursor = conn.cursor()


#    cursor.execute("INSERT INTO `{}`

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


### #------------------------------------------------------------------------
### DELETE
### #------------------------------------------------------------------------
import colorama
import inspect
import datetime




class Decorator(object):
    """
    Abstract Base Class: Decorator
    This stores the decorator information, such as the name (__decor__) and
    the docstring (__decordoc__)
    """

    # This is needed so that Decorator is an Abstract Base Class
    __metaclass__ = abc.ABCMeta

    def __init__(self, func, *args):
        self.func = func

        if inspect.isfunction(self.func):
            self.__name__ = self.func.__name__

        elif inspect.isclass(self.func):
            self.__name__ = self.func.__class__.__name__

        elif inspect.ismethod(self.func):
            self.__name__ = self.func.__name__

        # Create the new attributes for __decor__ and __decordoc__
        self._set_decor()
        self._set_decordoc()
        self._set_doc()

    def _set_decor(self):
        """ Sets the __decor__ attribute to the decorator name """
        # functions = methods & classes = string repr. of method/class
        self.__decor__ = self.func.__decor__ = self.__str__()

    def _set_decordoc(self):
        """ Sets the __decordoc__ attribute to the decorator docscring """
        # functions = methods & classes = string repr. of method/class
        self.__decordoc__ = self.func.__decordoc__ = self.__doc__

    def _set_doc(self):
        """ Sets the __doc__ attribute to the funcion's docstring """
        self.__doc__ = self.func.__doc__

    def __get__(self, obj, objtype):
        """ Support instance methods. """
        @functools.wraps(self.func)
        def wrapper(*args, **kwargs):
            return self.func(obj, *args, **kwargs)
        setattr(obj, self.func.__name__, wrapper)
        return wrapper

    # force child classes to have a __call__ method
    @abc.abstractmethod
    def __call__(self):
        pass

    # force child classes to have a __str__ method
    @abc.abstractmethod
    def __str__(self):
        pass


class CodeTimer(object):
    """
    A Simple code execution timer.

    My attempt at making a simple code timer. The idea is that a user can
    just call this simple thing, once to start and once again to stop. Upon
    stopping, it prints out the time delta.

    Stop times are printed in Red, while lap times are printed in Cyan. Time
    differences, as provided by the ``delta()`` method, are printed in Yellow.

    Parameters:
    -------
    label : string
        An optional label for the timer. Will be displayed upon stopping or
        lapping the timer.

    Public Attributes:
    ------------------
    label : string
        The label for the timer instance.

    running : bool
        Returns ``True`` if the timer is currently running.

    start_t : datetime.datetime object
        The time, in seconds, that the timer was last started, as reported
        by the built-in time.clock() function. Returns ``None`` if the
        timer has never been started.

    stop_t : datetime.datetime object
        The time, in seconds, that the timer was last stopped, as reported
        by the built-in time.clock() function. Returns ``None`` if the
        timer has never been stopped.

    diff : float
        The time between the the last lap or stop event and the start event.
        Returns ``None`` if the timer has never been lapped or stopped.

    prev_t : datetime.datetime object
        The timestamp of the previous lap, start, or delta event. Returns
        ``None`` if the timer has never been started.

    Public Methods:
    ---------------
    start(self) :
        Start the timer.

    stop(self, override_label=None) :
        Stops the timer and prints out the elapsed time, optionally
        overriding the label temporarily. Returns the elapsed time as a
        datetime.timedelta object.

    reset(self) :
        Resets the timer and clears the last start_t, stop_t, and diff values.

    lap(self, override_label=None) :
        Prints out the current elapsed time, optionally overrideing the
        label temporarily. Returns the elapsed time as a
        datetime.timedelta object.

    delta(self, override_label=None) :
        Prints out the time delta between this call and the previous call
        of ``delta``, ``lap``, or ``start``. Returns the value as a
        datetime.timedelta object.

    Examples:
    --------
    Basic Usage:

    >>> ct = CodeTimer("my_label")
    >>> ct.start()
    >>> # code to time
    >>> ct.stop()           # doctest: +SKIP
    my_label: 13.2725267063 seconds.

    Printing out lap times:

    >>> ct = CodeTimer()
    >>> ct.start()
    >>> for _i in range(3):
    ...     ct.lap()        # doctest: +SKIP
    Current Exec: 6.99158129829 seconds.
    Current Exec: 6.9916975028 seconds.
    Current Exec: 6.99176305405 seconds.
    >>> ct.stop()           # doctest: +SKIP
    Exec time: 18.8153060201 seconds.
    """
    def __init__(self, label=None):
        """ __init__(self, label: string = None) -> CodeTimer """
        # Initialize class attributes
        self.label = label
        self.temp_label = None
        self.running = False
        self.start_t = None
        self.stop_t = None
        self.diff = None
        self.prev_t = None

    def __str__(self):
        return "Timer: {}".format(self.label)

    def start(self):
        """ Start the timer """
#        self.start_t = time.clock()
        self.start_t = datetime.datetime.utcnow()
        self.prev_t = self.start_t
        self.running = True

    def stop(self, override_label=None):
        """ Stop the timer and return and print the delta with label. """
        if override_label is None:
            # Use the class label for the timer
            self.temp_label = self.label
        else:
            # Use the temporary override label for the timer
            self.temp_label = override_label
        if not self.running:
            raise RuntimeError("Timer not started.")

        self.running = False
#        self.stop_t = time.clock()
        self.stop_t = datetime.datetime.utcnow()
        self.diff = self.stop_t - self.start_t
        if self.temp_label is None:
            print_red("Exec time: {diff}".format(diff=self.diff))
            print()
        else:
            print_red("{lbl}: {diff}".format(lbl=self.temp_label,
                                             diff=self.diff))
            print()
        return self.diff

    def reset(self):
        """ Reset the timer. """
        self.start_t = None
        self.stop_t = None
        self.diff = None
        self.prev_t = None
        self.start()

    def lap(self, override_label=None):
        """ Returns and prints out the current timer value. """
        if override_label is None:
            # Use the class label for the timer
            self.temp_label = self.label
        else:
            # Use the temporary override label for the timer
            self.temp_label = override_label
        if not self.running:
            raise RuntimeError("Timer not started.")

        self.running = True
#        self.stop_t = time.clock()
        self.stop_t = datetime.datetime.utcnow()
        self.prev_t = self.stop_t
        self.diff = self.stop_t - self.start_t
        if self.temp_label is None:
            cprint("Current Exec: {diff}".format(diff=self.diff),
                   'c')
            print()
        else:
            cprint("{lbl}: {diff}".format(lbl=self.temp_label,
                                          diff=self.diff),
                   'c')
            print()
        return self.diff

    def delta(self, override_label=None):
        """
        Prints out the time delta between this call and the previous
        call of ``delta``, ``lap`` or ``start``. Returns the value
        as a datetime.timedelta object.
        """
        if override_label is None:
            # Use the class label for the timer
            self.temp_label = self.label
        else:
            # Use the temporary override label for the timer
            self.temp_label = override_label
        if not self.running:
            raise RuntimeError("Timer not started.")

        self.running - True
#        self.stop_t = time.clock()
        self.stop_t = datetime.datetime.utcnow()
        self.diff = self.stop_t - self.prev_t
        self.prev_t = self.stop_t
        if self.temp_label is None:
            cprint("Delta: {diff}".format(diff=self.diff),
                   'y')
            print()
        else:
            cprint("{lbl}: {diff}".format(lbl=self.temp_label,
                                          diff=self.diff),
                   'y')
            print()
        return self.diff

def print_red(text):
    """ Prints text as bright red """
    cprint(text, 'red')

def cprint(text, color, end='\n'):
    """ Prints text as the specified color. Accepts RGB, CMYK, and White. """
    colors = {'r': colorama.Fore.RED,
              'red': colorama.Fore.RED,
              'g': colorama.Fore.GREEN,
              'green': colorama.Fore.GREEN,
              'b': colorama.Fore.BLUE,
              'blue': colorama.Fore.BLUE,
              'c': colorama.Fore.CYAN,
              'cyan': colorama.Fore.CYAN,
              'y': colorama.Fore.YELLOW,
              'yellow': colorama.Fore.YELLOW,
              'm': colorama.Fore.MAGENTA,
              'magenta': colorama.Fore.MAGENTA,
              'k': colorama.Fore.BLACK,
              'black': colorama.Fore.BLACK,
              'w': colorama.Fore.WHITE,
              'white': colorama.Fore.WHITE}
    colorama.init(strip=False)      # for Spyder: don't strip format chars
    print(colors[color.lower()] + colorama.Style.BRIGHT + text, end=end)
    print(colorama.Style.RESET_ALL, end='')
    colorama.deinit()

class Timed(Decorator):
    """
    Decorator.
    Times a given function execution.
    """
    def __init__(self, func):
        """ Init instance attributes """
        Decorator.__init__(self, func)
        self.codetimer = CodeTimer(self.func.__name__)

    def __call__(self, *args, **kwargs):
        """ Actually call the function """
        self.codetimer.start()
        result = self.func(*args, **kwargs)
        self.codetimer.stop()
        return result

    def __str__(self):
        return "Timed"





def db_query2(conn, query, *args):
    with closing(conn.cursor()) as cursor:
        cursor.execute(query, args)
        retval = cursor.fetchall()
    return retval

def db_query3(cursor, query, *args):
    cursor.execute(query, args)
    return cursor.fetchall()

@Timed
def test():
    fn = "C:\\WinPython34_x64\\projects\\github\\PyBank\\pybank\\test_database.db"
    query = "SELECT * FROM acct WHERE id=1"
    for _ in range(5000):
        db_query(fn, query)

@Timed
def test2():
    fn = "C:\\WinPython34_x64\\projects\\github\\PyBank\\pybank\\test_database.db"
    query = "SELECT * FROM acct WHERE id=1"
    conn = sqlite3.connect(fn)
    for _ in range(5000):
        db_query2(conn, query)
    conn.close()

@Timed
def test3():
    fn = "C:\\WinPython34_x64\\projects\\github\\PyBank\\pybank\\test_database.db"
    query = "SELECT * FROM acct WHERE id=1"
    conn = sqlite3.connect(fn)
    cursor = conn.cursor()
    for _ in range(5000):
        db_query3(cursor, query)
    cursor.close()
    conn.close()


### #------------------------------------------------------------------------
### END DELETE
### #------------------------------------------------------------------------

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

    test3()
    test2()
#    test()

    a = db_query_single(DATABASE,
                                     "SELECT COUNT(*) FROM v_ledger_0")[0]
    print(a)

