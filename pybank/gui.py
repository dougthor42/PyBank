# -*- coding: utf-8 -*-
# pylint: disable=E1101, C0330
#   E1101 = Module X has no Y member
"""
GUI components for PyBank.

Created on Tue May 12 13:21:37 2015

Usage:
    gui.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""
# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
import logging
#import sys
import decimal
#import os.path as osp
from enum import Enum
#import random
import datetime

# Third Party
import wx
import wx.grid
import wx.lib.plot as wxplot
import numpy as np

try:
    from agw import foldpanelbar as fpb
except ImportError:
    import wx.lib.agw.foldpanelbar as fpb

# Package / Application
try:
    # Imports used by unit test runners
    from . import pbsql
    from . import plots
    from . import utils
    from . import crypto
    from . import gui_utils
    from . import sa_orm_transactions
#    from . import __init__ as __pybank_init
    from . import (__project_name__,
                   __version__,
                   )

    logging.debug("Imports for UnitTests")
except SystemError:
    try:
        # Imports used by Spyder
        import pbsql
        import plots
        import utils
        import crypto
        import gui_utils
        import sa_orm_transactions
#        import __init__ as __pybank_init
        from __init__ import (__project_name__,
                              __version__,
                              )

        logging.debug("Imports for Spyder IDE")
    except ImportError:
         # Imports used by cx_freeze
        from pybank import pbsql
        from pybank import plots
        from pybank import utils
        from pybank import crypto
        from pybank import gui_utils
        from pybank import sa_orm_transactions
#        from pybank import __init__ as __pybank_init
        from pybank import (__project_name__,
                            __version__,
                            )

        logging.debug("imports for Executable")


# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------

LEDGER_COLOR_ROW_NEW = wx.Colour(240, 240, 240, 255)
LEDGER_COLOR_ROW_ODD = wx.Colour(255, 255, 255, 255)
LEDGER_COLOR_ROW_EVEN = wx.Colour(255, 255, 204, 255)
LEDGER_COLOR_VALUE_NEGATIVE = wx.Colour(255, 0, 0, 255)
LEDGER_COLOR_VALUE_POSITIVE = wx.Colour(0, 0, 0, 255)
DATABASE = "test_database.db"

TITLE_TEXT = "{} v{}".format(__project_name__, __version__)

# ---------------------------------------------------------------------------
### Main GUI
# ---------------------------------------------------------------------------

class MainApp(object):
    """ Main App """
    def __init__(self):
        self.app = wx.App()

        self.frame = MainFrame(TITLE_TEXT, (1250, 700))

        self.frame.Show()
        self.app.MainLoop()


class MainFrame(wx.Frame):
    """ Main Window of the PyBank program """
    def __init__(self, title, size):
        wx.Frame.__init__(self, None, wx.ID_ANY, title=title, size=size)

        # Set up some timers for backup and write-to-db
        self.write_db_timer = wx.Timer(self)
        self.write_db_timer.Start(1000)
        logging.debug("Write-to-database timer started")

        self.encryption_timer = wx.Timer(self)
        self.encryption_timer.Start(5000)
        logging.debug("Encryption timer started")

        self._init_ui()

    def _init_ui(self):
        """ Initi UI Components """
        # Create the menu bar and bind events
        self.menu_bar = wx.MenuBar()
        self._create_menus()
        self._bind_events()

        # Initialize default states
        self._set_defaults()

        # Set the MenuBar and create a status bar
        self.SetMenuBar(self.menu_bar)
        self.CreateStatusBar()

        self.panel = MainPanel(self)

        self.ledger = self.panel.panel2.ledger_page.ledger

    def _create_menus(self):
        """ Create each menu for the menu bar """
        # TODO: Switch to wx.RibbonBar? It looks pretty nice.
        self._create_file_menu()
        self._create_edit_menu()
        self._create_view_menu()
        self._create_tools_menu()
        self._create_options_menu()
        self._create_help_menu()

    def _create_file_menu(self):
        """
        Creates the File menu.

        wxIDs:
        ------
        + 101: New
        + 102: Open
        + 103: Exit

        """
        # Create the menu and items
        self.mfile = wx.Menu()
        self.mf_new = wx.MenuItem(self.mfile, 101, "&New\tCtrl+N",
                                  "Create a new PyBank file")
        self.mf_open = wx.MenuItem(self.mfile, 102, "&Open\tCtrl+O",
                                   "Open a PyBank file")
        self.mf_close = wx.MenuItem(self.mfile, 104, "&Close\tCtrl+W",
                                    "Close the current PyBank file.")

        self.mf_open_ofx = wx.MenuItem(self.mfile, 105, "Open OFX File",
            "Open an existing OFX and append to the current ledger")


        self.mf_exit = wx.MenuItem(self.mfile, 103, "&Exit\tCtrl+Q",
                                   "Exit the application")

        # Add menu items to the menu
        self.mfile.Append(self.mf_new)
        self.mfile.Append(self.mf_open)
        self.mfile.Append(self.mf_close)
        self.mfile.AppendSeparator()
        self.mfile.Append(self.mf_open_ofx)
        self.mfile.AppendSeparator()
        self.mfile.Append(self.mf_exit)
        self.menu_bar.Append(self.mfile, "&File")

    def _create_edit_menu(self):
        """
        Creates the Edit menu

        wxIDs:
        ------
        + 201: ???
        + 202: ???

        """
        # Create the menu and items
        self.medit = wx.Menu()
        self.me_temp = wx.MenuItem(self.medit, 201, "&Temp", "TempItem")

        # Add menu items to the menu
        self.medit.Append(self.me_temp)
        self.menu_bar.Append(self.medit, "&Edit")

    def _create_view_menu(self):
        """
        Creates the View menu.

        wxIDs:
        ------
        + 301: ???
        + 302: ???
        """
        # Create the menu and items
        self.mview = wx.Menu()
        self.mv_l = wx.Menu()
        self.mv_temp = wx.MenuItem(self.mview, 301, "&Temp", "TempItem")
        # TODO: There's gotta be a way to auto-populate this menu from the tbl
        self.mv_l_date = wx.MenuItem(self.mv_l, 30201, "Date", "",
                                     wx.ITEM_CHECK)
        self.mv_l_enter_date = wx.MenuItem(self.mv_l, 30202, "Enter Date", "",
                                           wx.ITEM_CHECK)
        self.mv_l_checknum = wx.MenuItem(self.mv_l, 30203, "Check Number", "",
                                         wx.ITEM_CHECK)
        self.mv_l_payee = wx.MenuItem(self.mv_l, 30204, "Payee", "",
                                      wx.ITEM_CHECK)
        self.mv_l_dlpayee = wx.MenuItem(self.mv_l, 30205, "Downloaded Payee",
                                        "", wx.ITEM_CHECK)
        self.mv_l_memo = wx.MenuItem(self.mv_l, 30206, "Memo", "",
                                     wx.ITEM_CHECK)
        self.mv_l_cat = wx.MenuItem(self.mv_l, 30207, "Category", "",
                                    wx.ITEM_CHECK)
        self.mv_l_label = wx.MenuItem(self.mv_l, 30208, "Label",
                                      "", wx.ITEM_CHECK)
        self.mv_l_amount = wx.MenuItem(self.mv_l, 30209, "Amount", "",
                                       wx.ITEM_CHECK)
        self.mv_l_balance = wx.MenuItem(self.mv_l, 30210, "Balance", "",
                                        wx.ITEM_CHECK)

        # Add menu items to the menu
        self.mv_l.Append(self.mv_l_date)
        self.mv_l.Append(self.mv_l_enter_date)
        self.mv_l.Append(self.mv_l_checknum)
        self.mv_l.Append(self.mv_l_payee)
        self.mv_l.Append(self.mv_l_dlpayee)
        self.mv_l.Append(self.mv_l_memo)
        self.mv_l.Append(self.mv_l_cat)
        self.mv_l.Append(self.mv_l_label)
        self.mv_l.Append(self.mv_l_amount)
        self.mv_l.Append(self.mv_l_balance)

        self.mview.Append(self.mv_temp)
        self.mview.Append(302, "Ledger Columns", self.mv_l)
        self.menu_bar.Append(self.mview, "&View")

    def _create_tools_menu(self):
        """
        """
        # Create the menu and items
        self.mtools = wx.Menu()
        self.mt_accounts = wx.MenuItem(self.mtools, 401, "&Accounts",
                                       "Add and modify accounts")

        # Add menu items to the menu
        self.mtools.Append(self.mt_accounts)
        self.menu_bar.Append(self.mtools, "&Tools")

    def _create_options_menu(self):
        """
        """
        # Create the menu and items
        self.mopts = wx.Menu()
        self.mo_accounts = wx.MenuItem(self.mopts, 501, "&Temp",
                                       "No idea yet")

        # Add menu items to the menu
        self.mopts.Append(self.mo_accounts)
        self.menu_bar.Append(self.mopts, "&Options")

    def _create_help_menu(self):
        """
        """
        # Create the menu and items
        self.mhelp = wx.Menu()
        self.mh_about = wx.MenuItem(self.mhelp, 601, "&About",
                                    "Infomation about PyBank")

        # Add menu items to the menu
        self.mhelp.Append(self.mh_about)
        self.menu_bar.Append(self.mhelp, "&Help")

    def _set_defaults(self):
        """
        """
        self.mv_l_date.Check(True)
        self.mv_l_enter_date.Check(False)
        self.mv_l_checknum.Check(True)
        self.mv_l_payee.Check(True)
        self.mv_l_dlpayee.Check(True)
        self.mv_l_memo.Check(False)
        self.mv_l_cat.Check(True)
        self.mv_l_label.Check(True)
        self.mv_l_amount.Check(True)
        self.mv_l_balance.Check(True)

    def _bind_events(self):
        """ Bind all initial events """
        # File Menu
        self.Bind(wx.EVT_MENU, self._on_new, id=101)
        self.Bind(wx.EVT_MENU, self._on_open, id=102)
        self.Bind(wx.EVT_MENU, self._on_close, id=104)
        self.Bind(wx.EVT_MENU, self._on_quit, id=103)
        self.Bind(wx.EVT_MENU, self._on_open_ofx, id=105)

        # Edit Menu
#        self.Bind(wx.EVT_MENU, self._on_edit_menu1)

        # View Menu
#        self.Bind(wx.EVT_MENU, self._nothing)
        self.Bind(wx.EVT_MENU, self._on_toggle_ledger_col, id=30201, id2=30210)

        # Tools Menu

        # Options Menu

        # Help Menu

        # Timers
        self.Bind(wx.EVT_TIMER, self._on_encryption_timer, self.encryption_timer)
        self.Bind(wx.EVT_TIMER, self._on_write_db_timer , self.write_db_timer)

    def _on_quit(self, event):
        """ Execute quit actions """
        logging.debug("on quit")
        self.Close(True)

    def _on_open(self, event):
        """ Open a file """
        logging.debug("on open")

        dialog = wx.FileDialog(self,
                               "Choose a PyBank datatbase file to open",
                               ".",
                               "",
                               "PyBank database (*.pybank)|*.pybank",
                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
                               )

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        path = dialog.GetPath()

        logging.info("Opening file: `{}`".format(path))

        self.ledger._setup()
        self.ledger.table._update_data()
        self.ledger._format_table()

    def _on_open_ofx(self, event):
        logging.debug("on open ofx")

        dialog = wx.FileDialog(self,
                               "Choose a OFX file to open",
                               ".",
                               "",
                               "OFX files (*.ofx)|*.ofx",
                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
                               )

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        path = dialog.GetPath()

        logging.info("Opening OFX file: `{}`".format(path))


    def _on_new(self, event):
        """ Create a new file """
        logging.debug("on new")
        logging.info("Creating new file")
        logging.info("(Not yet implemented)")

    def _on_close(self, event):
        """ Create a new file """
        logging.debug("on close")
        logging.info("Closing current file.")

        self.ledger.table.data = [[]]

        self.ledger.ClearGrid()
        self.ledger._format_table()

    def _on_toggle_ledger_col(self, event):
        """ Toggles a ledger column on or off """
        col_num = event.Id - 30200      # Ledger columns are 0-indexed
                                        # but we always show the # col
            # I don't rememer where 30200 comes from, but it's needed
            # to make col_num 0-indexed.
        new_val = event.IsChecked()
        self.panel.panel2.ledger_page.ledger.SetColumnShown(col_num, new_val)

    def _on_encryption_timer(self, event):
        logging.debug("Encryption Timer event!")

    def _on_write_db_timer(self, event):
        logging.debug("Write_db_timer event!")


class MainPanel(wx.Panel):
    """ Main Panel; contains all other panels and elements """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent



        self._init_ui()

    def _init_ui(self):
        """ Initialize the UI Components """
        # Create items
        self.splitter = wx.SplitterWindow(self, wx.ID_ANY,
                                          style=wx.SP_LIVE_UPDATE,
                                          )

#        self.panel1 = AccountListTree(self.splitter)
        self.panel1 = AccountList(self.splitter)
        self.panel2 = MainNotebook(self.splitter)

        # Set up the splitter attributes
        self.splitter.SetMinimumPaneSize(100)
        self.splitter.SplitVertically(self.panel1, self.panel2, 200)

        # Create layout manager, add items, and set sizer.
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.splitter, 1, wx.EXPAND)
        self.SetSizer(self.hbox)


class SamplePanel(wx.Panel):
    """
    Just a simple test window to put into the splitter.
    """
    def __init__(self, parent, colour, label):
        wx.Panel.__init__(self, parent, style=wx.BORDER_SUNKEN)
        self.SetBackgroundColour(colour)
        wx.StaticText(self, -1, label, (5, 5))


class SamplePlotPanel(wx.Panel):
    """
    Example plotting using the built-in wx.lib.plot (wxplot).

    Keeps things smaller because it doesn't require numpy or matplotlib,
    but means more coding and looks a little rougher.
    """
    def __init__(self, parent, colour, label):
        wx.Panel.__init__(self, parent, style=wx.BORDER_SUNKEN)
        self.SetBackgroundColour(colour)
        title = wx.StaticText(self, -1, label, (5, 5))

        self.fake_x_data = [1, 2, 3, 4, 5, 6, 7]
        self.fake_y_data = [15, 13.6, 18.8, 12, 2, -6, 25]

        self.client = wxplot.PlotCanvas(self, size=(400, 300))

        # Then set up how we're presenting the data. Lines? Point? Color?
        tdata = list(zip(self.fake_x_data, self.fake_y_data))

        line = wxplot.PolyLine(tdata,
                               colour='red',
                               width=2,
                               drawstyle='steps-post',
                               )

        data = wxplot.PolyMarker(tdata,
                                 legend="Green Line",
                                 colour='red',
                                 width=4,
                                 size=1,
                                 marker='square',
#                                 style=wx.PENSTYLE_SOLID,
                                 )

        plot = wxplot.PlotGraphics([line, data],
                                   title="Title",
                                   xLabel="X label",
                                   yLabel="Monies",
                                   )
        self.plot = plot

        self.client.GridPen = wx.Pen(wx.Colour(230, 230, 230, 255))
        self.client.EnableGrid = True
        self.client.Draw(plot)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(title, 0)
        self.sizer.Add(self.client, 0)
        self.SetSizer(self.sizer)


class NotebookPages(Enum):
    """
    Contains the notebook pages number-name link
    """
    summary = 0
    ledger = 1
    plots = 2
    wxmplot = 3
    wxlibplot = 4


class MainNotebook(wx.Notebook):
    """
    Notebook container for most everything.

    Contains tabs for:

    + Summary
    + Ledger
    + Scheduled Transactions
    + Projected Balances

    And perhaps other stuff.
    """
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent)
        self.parent = parent

        self._init_ui()

    def _init_ui(self):
        """ Initialize UI components """
        p0 = SamplePanel(self, "yellow", "Summary Page")
        self.AddPage(p0, "Summary")

        self.ledger_page = LedgerPanel(self)
        self.AddPage(self.ledger_page, "Ledger")

        p4 = SamplePlotPanel(self, "orange", "Plotting with wx.lib.plot")
        self.AddPage(p4, "Even more stuff")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_page_changed)
#        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._on_page_changing)

        # Show the ledger at start (SetSelection generates events)
        self.SetSelection(NotebookPages.ledger.value)

    def _on_page_changed(self, event):
        """
        Event fires *after* the page is changed.

        old is the previous page
        new is the page we changed to
        sel is which, if any, page was selected.
            For example, if I use SetSelection(2), sel might be 1 or 0.
        """
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        log_txt = "Page Changed: old: {}, new: {}, sel: {}"
        logging.debug(log_txt.format(old, new, sel))
        if new == NotebookPages.plots.value:
            self._change_to_plots()

    def _on_page_changing(self, event):
        """
        Event fires *before* the page is changed.

        Note how old, new, and sel are all the same.

        This event can be vetoed.
        """
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        log_txt = "Page Changing: old: {}, new: {}, sel: {}"
        logging.debug(log_txt.format(old, new, sel))

    def _change_to_plots(self):
        """
        Executes when changing to a plot page.

        Fires the plot.draw() method.
        """
        # TODO: Change this data grab to sql.
        d = self.ledger_page.ledger.GetTable().data
        x = np.arange(1, len(d) + 1)
#        y = [random.uniform(-1, 1) + _x for _x in x]
        y = np.array([x[10] for x in d], dtype=np.float)
        client = self.GetPage(NotebookPages.plots.value).client
        client.Clear()    # XXX: Not working (panel not updating?)
#        plot.draw(x, y, 'r')

        tdata = list(zip(x, y))

        line = wxplot.PolyLine(tdata,
                               colour='red',
                               width=2,
                               drawstyle='steps-post',
                               )

        data = wxplot.PolyMarker(tdata,
                                 legend="Green Line",
                                 colour='red',
                                 width=4,
                                 size=1,
                                 marker='square',
#                                 style=wx.PENSTYLE_SOLID,
                                 )

        plot = wxplot.PlotGraphics([line, data],
                                   title="Title",
                                   xLabel="X label",
                                   yLabel="Monies",
                                   )

        client.GridPen = wx.Pen(wx.Colour(230, 230, 230, 255))
        client.EnableGrid = True
        client.Draw(plot)


#        pareto = self.GetPage(NotebookPages.plots.value).pareto
#        pareto.clear()
#        y = np.array([x[4] for x in d], dtype=np.str)
#        pareto.draw(y)


class LedgerPanel(wx.Panel):
    """
    The transaction ledger

    Should contain the following columns:

    + Transaction Date
    + Entered Date
    + CheckNum
    + Payee DisplayName
    + Downloaded Payee
    + Memo
    + Category
    + Label
    + Amount  # do I want separate payment/income columns? probably red/black
    + Balance
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent

        self._init_ui()

    def _init_ui(self):
        """ Initialize UI components """
        self.header_bar = LedgerHeaderBar(self)
        self.ledger = LedgerGrid(self)
        self.summary_bar = LedgerSummaryBar(self)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.header_bar, 0, wx.EXPAND)
        self.vbox.Add(self.ledger, 1, wx.EXPAND)
        self.vbox.Add(self.summary_bar, 0, wx.EXPAND)
        self.SetSizer(self.vbox)


class LedgerGridBaseTable(wx.grid.GridTableBase):
    """
    """
    # -----------------------------------------------------------------------
    ### Class Constants
    # -----------------------------------------------------------------------
    # Define the columns ledger columns and how they map to the ledger view
    # in the database

    # (ledger column name, associated database view column name,
    #  ledger column type, ledger column width)

    col_tid = ("tid", "transaction_id",
               wx.grid.GRID_VALUE_STRING, 30,
               )

    col_date = ("Date", "date",
                wx.grid.GRID_VALUE_TEXT, 100,
                )

    col_enter_date = ("Date Entered", "enter_date",
                      wx.grid.GRID_VALUE_TEXT, 100,
                      )

    col_checknum = ("CheckNum", "check_num",
                    wx.grid.GRID_VALUE_TEXT, 80,
                    )

    col_payee = ("Payee", "Payee",
                 wx.grid.GRID_VALUE_TEXT, 120,
                 )

    col_dl_payee = ("Downloaded Payee", "DownloadedPayee",
                    wx.grid.GRID_VALUE_TEXT, 120,
                    )

    col_memo = ("Memo", "Memo",
                wx.grid.GRID_VALUE_TEXT, 150,
                )

    col_category = ("Category", "Category",
                    wx.grid.GRID_VALUE_TEXT, 180,
                    )

    col_label = ("Label", "TransactionLabel",
                 wx.grid.GRID_VALUE_TEXT, 160,
                 )

    col_amount = ("Amount", "Amount",
                  wx.grid.GRID_VALUE_TEXT, 80,
                  )

    col_balance = ("Balance", None,
                   wx.grid.GRID_VALUE_TEXT, 80,
                   )

    columns = (col_tid,
               col_date,
               col_enter_date,
               col_checknum,
               col_payee,
               col_dl_payee,
               col_memo,
               col_category,
               col_label,
               col_amount,
               col_balance,
               )

    # -----------------------------------------------------------------------
    ### Magic Methods
    # -----------------------------------------------------------------------
    def __init__(self, parent):
        wx.grid.GridTableBase.__init__(self)
        self.parent = parent
        self.column_labels, self.col_types = self._set_columns()
        self.data = []
            # TODO: move amount and balance to numpy arrays?

        # flag for when the data has been changed with respect to the database
        self.data_is_modified = False

        self._update_data()


    # -----------------------------------------------------------------------
    ### Override Methods
    # -----------------------------------------------------------------------
    def GetNumberRows(self):
        rows = len(self.data)
#        rows = pbsql.db_query_single(DATABASE,
#                                     "SELECT COUNT(*) FROM v_ledger_0")[0]
        return rows + 1
#        return len(self.data) + 1

    def GetNumberCols(self):
        return len(self.data[0])

    def IsEmptyCell(self, row, column):
#        logging.debug("IsEmptyCell(row={}, col={})".format(row, column))
        try:
            return not self.data[row][column]
        except IndexError:
            return True

    def GetValue(self, row, col):
        """
        Get the cell value from the data or database.

        Override Method

        Is called on every cell at init and then again when cells are
        clicked.
        """
#        logging.debug("Getting value of r{}c{}".format(row, column))
        try:
            value = self.data[row][col]
            if value is None or value == 'None':
                return ''
            else:
                return value
        except IndexError:
            return ''
#        return self._get_value(row, col)

    def _get_value(self, row, col):
        """
        Private logic for the GetValue() override method.

        ~~The goal here is that we never copy data from the database to a
        python object, we just look directly at the database (and DB view)
        for the value.~~

        Nope, just kidding. I think it's actually better to copy to a python
        object. Why? Because then we aren't actively acting on the database
        which means
            1) fewer transactions
            2) easier to revert changes
            3) don't have to worry about invalid data until we
               try and write to DB



        What this means is that I have to know the mapping of column number
        to column name to associated table column name. This logic will
        also handle things such as translating the category to a nested list
        (like "Expense:Food:Fast Food") and having null values show up as
        blanks.

        For now, I'm just going to brute-force this thing.
        """

        # TODO: come up with a better way. Brute-force is not extensible.
        row_data = sa_orm_transactions.query_view()[row]
        if col == 0:                # transaction_id
            return row_data.transaction_id
        elif col == 1:              # Date
            return row_data.date
        elif col == 2:              # Date Entered
            return row_data.enter_date
        elif col == 3:              # CheckNum
            return row_data.check_num
        elif col == 4:
            return row_data.Payee
        elif col == 5:
            return row_data.DownloadedPayee
        elif col == 6:
            return row_data.Memo
        elif col == 7:
            return row_data.Category
        elif col == 8:
            return row_data.TransactionLabel
        elif col == 9:
            return row_data.Amount
        elif col == 10:
            return 0

    def SetValue(self, row, col, value):
        """
        Sets the value of a cell.

        Override Method.
        """
        self._set_value(row, col, value)

    # for sqlite backend
#    def _set_value(self, row, col, value):
#        """
#        Updates the database with the value of the cell.
#
#        # TODO: If updating an existing payee name, then we
#        #       add to the display_name table.
#        #       If adding a new payee name, check it against the payee table
#        #       Add if needed, otherwise...?
#        """
#        logging.debug("Setting r{}c{} to `{}`".format(row, col, value))
#        try:
#            # update database entry
#            # gotta get the tid and send *that* to the update method
#            # to account for deleted entries.
#            tid = self.data[row][0]
#            self.ledger_view.update_transaction(tid, col, value)
#        except IndexError:
#            # add a new row
#            logging.debug("Adding a new row")
#            self.ledger_view.insert_row()
#            self._update_data()         # Must come before _set_value()
#            self._set_value(row, col, value)
#
#            # tell grid we've added a row
#            action = wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED
#            msg = wx.grid.GridTableMessage(self, action, 1)
#            self.GetView().ProcessTableMessage(msg)
#            self.parent._format_table()
#        else:
#            # run this if no errors
#            self._update_data()
#            # _update_data() does not update the balance for all rows. hmm...
#            # Update values
#            action = wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES
#            msg = wx.grid.GridTableMessage(self, action)
#            self.GetView().ProcessTableMessage(msg)
#            self.parent._format_table()

    # for SQLAlchemy backend
    def _set_value(self, row, col, value):
        """
        Updates the data value for a given cell.

        Does not attempt to update the database
        """
        logging.debug("Setting r{}c{} to `{}`".format(row, col, value))
        try:
            logging.debug("trying to update row")
            logging.debug("Previous: {}".format(self.data[row]))
            self.data[row][col] = value
        except IndexError:
            # add a new row
            logging.debug("Update failed. Adding new row")
            self.data.append([None] * self.GetNumberCols())
            self.data[row][0] = str(int(self.data[row - 1][0]) + 1)
            self.data[row][col] = value

            # tell the grid that we've added a row
            logging.debug("GRIDTABLE_NOTIFY_ROWS_APPENDED")
            action = wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED
            msg = wx.grid.GridTableMessage(self, action, 1)
#            self.GetView().ProcessTableMessage(msg)
#            self.parent._format_table()
        else:       # run only if no *unhandled* errors
            # tell the grid to display the new values
            logging.debug("GRIDTABLE_REQUEST_VIEW_GET_VALUES")
            action = wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES
            msg = wx.grid.GridTableMessage(self, action)
#            self.GetView().ProcessTableMessage(msg)
#            self.parent._format_table()
        finally:    # always runs
            pass

        self.GetView().ProcessTableMessage(msg)
        self.parent._format_table()

        self.data_is_modified = True

    def GetColLabelValue(self, column):
        return self.column_labels[column]

    def GetTypeName(self, row, column):
        return self.col_types[column]

    def CanGetValueAs(self, row, column, type_name):
        column_type = self.col_types[column].split(":")[0]
        return type_name == column_type

    def CanSetValueAs(self, row, column, type_name):
        return self.CanGetValueAs(row, column, type_name)

    # -----------------------------------------------------------------------
    ### Private Methods
    # -----------------------------------------------------------------------

    def _set_columns(self):
        """
        Sets the columns for the ledger.
        """
        # TODO: make column order depend only on the DB view
        labels = [_i[0] for _i in self.columns]
        types = [_i[2] for _i in self.columns]

        for _i, title in enumerate(labels):
            self.SetColLabelValue(_i, title)

        return (labels, types)

    def _update_data(self):
        # grab the table data from the database
        self.data = []

        # convert the query results to something usable by the grid
        # Also calculate the running balancefor the view.
        # TODO: I hate this - come up with an alternate solution
        starting_bal = decimal.Decimal(200)
        balance = starting_bal
        for row_num, row_data in enumerate(sa_orm_transactions.query_view()):
            data_dict = row_data.__dict__
            row_values = []
            for col_num, (_, name, _, _) in enumerate(self.columns):
                if name is None:
                    continue

                if isinstance(data_dict[name], datetime.date):
                    row_values.append(str(data_dict[name]))
                elif col_num == 0 or col_num == 3:
                    row_values.append(str(data_dict[name]))
                else:
                    row_values.append(data_dict[name])

            balance += decimal.Decimal(row_values[-1])
            row_values[-1] = str(row_values[-1])
            row_values.append(str(balance))
            self.data.append(row_values)

#        print(list(x for x, _, _, _ in self.columns))
#        for row in data:
#            print(row)


class LedgerGrid(wx.grid.Grid):
    """
    """
    def __init__(self, parent):
        logging.debug("Initializing LedgerGrid")
        wx.grid.Grid.__init__(self, parent, wx.ID_ANY)

        self._setup()

#        self.table = LedgerGridBaseTable(self)
#
#        self.SetTable(self.table, True)
#
#        self.SetRowLabelSize(30)
#        self.SetMargins(0, 0)
#        self.AutoSizeColumns(True)
#
#        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK,
#                  self._on_left_dclick,
#                  self)
#
#        self._format_table()

    def _setup(self):
        self.table = LedgerGridBaseTable(self)

        self.SetTable(self.table, takeOwnership=True)

        self.SetRowLabelSize(30)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(True)

        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK,
                  self._on_left_dclick,
                  self)

        self._format_table()

    def _format_table(self):
        """ Formats all table properties """
        logging.debug("Formatting table")
        self._color_rows()
        self._align_columns()
        self._color_dollars()

    def _color_rows(self):
        """ Color alternating rows and color the last row light grey """
        logging.debug("Coloring rows")
        num_rows = self.GetNumberRows()
        for row in range(num_rows):
            attr = wx.grid.GridCellAttr()
            if row == num_rows - 1:
                attr.SetBackgroundColour(LEDGER_COLOR_ROW_NEW)
            elif row % 2 == 0:
                attr.SetBackgroundColour(LEDGER_COLOR_ROW_EVEN)
            else:
                attr.SetBackgroundColour(LEDGER_COLOR_ROW_ODD)
            self.SetRowAttr(row, attr)

    def _align_columns(self):
        """ Sets the alignment for each column """
        logging.debug("Setting column alignment")
        num_cols = self.GetNumberCols()
        for column in range(num_cols):
            attr = wx.grid.GridCellAttr()
            if column in (3, 9, 10):
                attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
            else:
                attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
            self.SetColAttr(column, attr)

    def _color_dollars(self):
        """ Colors negative amounts and balances as red """
        logging.debug("Coloring negative balances")
        num_rows = self.GetNumberRows() - 1
        for row in range(num_rows):
            for col in (9, 10):
                try:
                    val = float(self.GetCellValue(row, col))
                except ValueError:
                    val = 0
                if val < 0:
                    self.SetCellTextColour(row, col,
                                           LEDGER_COLOR_VALUE_NEGATIVE)
                else:
                    self.SetCellTextColour(row, col,
                                           LEDGER_COLOR_VALUE_POSITIVE)


    def _on_left_dclick(self, event):
        # TODO: get cell coord from event
        logging.debug("double left click on cell {}".format(event))
        if self.CanEnableCellControl():
            self.EnableCellEditControl()


# TODO: Add some way to highlight which account is active. A button, mayhaps?
class AccountList(wx.Panel):
    """ List of the accounts """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent

        self._account_list = None
        self._account_list = ["acct1", "acct2", "acct3", "acct4"]

        self._account_groups = ["Group1", "Group2"]

        self._init_ui()

    def _init_ui(self):
        """ Initialize UI components """
        # Set style info for the FoldPanelBar (CaptionBars)
        self.style = fpb.CaptionBarStyle()
        self.style.SetCaptionStyle(fpb.CAPTIONBAR_GRADIENT_H)
        color1 = wx.Colour((0, 255, 255))
        color2 = wx.Colour((255, 255, 255))
        self.style.SetFirstColour(color1)
        self.style.SetSecondColour(color2)

        # Create items
        titlefont = wx.Font(16,
                            wx.FONTFAMILY_DEFAULT,
                            wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD,
                            )
        self.title = wx.StaticText(self, wx.ID_ANY,
                                   label="Accounts",
                                   size=(-1, -1),
                                   style=wx.ALIGN_CENTER,
                                   )
        self.title.SetFont(titlefont)

        # Create the entire FoldPanelBar
        self._bar = fpb.FoldPanelBar(self, wx.ID_ANY, size=(500, -1))

        # Create the 1st fold panel.
        self.fp_1 = self._bar.AddFoldPanel("caption", collapsed=False,
                                           cbstyle=self.style)

        # Create items that belong to 1st fold panel
        # Note that items must be created then added immediatly.
        text1 = wx.StaticText(self.fp_1, wx.ID_ANY, label="Hello")
        self._bar.AddFoldPanelWindow(self.fp_1, text1)
        text2 = wx.StaticText(self.fp_1, wx.ID_ANY, label="Goodbye")
        self._bar.AddFoldPanelWindow(self.fp_1, text2)

        # Create 2nd fold panel
        self.fp_2 = self._bar.AddFoldPanel("2nd panel", collapsed=False,
                                           cbstyle=self.style)

        # create items to add to the 2nd fold panel
        text3 = wx.StaticText(self.fp_2, wx.ID_ANY, label="Panel2 text3")
        self._bar.AddFoldPanelWindow(self.fp_2, text3)
        text4 = wx.StaticText(self.fp_2, wx.ID_ANY, label="Panel2 text4")
        self._bar.AddFoldPanelWindow(self.fp_2, text4)

        # Create the layout managers, add items, and set the sizer
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self._bar, 0, wx.EXPAND)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.title, 0, wx.EXPAND)
        self.vbox.Add((-1, 3), 0, wx.EXPAND)
        self.vbox.Add(self.hbox, 1, wx.EXPAND)

        self.SetSizer(self.vbox)


class AccountListTree(wx.Panel):
    """
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
#        wx.gizmos.TreeListCtrl.__init__(self, parent, wx.ID_ANY)

        self._init_ui()

    def _init_ui(self):

        tc_style = (wx.TR_DEFAULT_STYLE
                    | wx.TR_HAS_BUTTONS
#                    | wx.TR_HAS_VARIABLE_ROW_HEIGHT
#                    | wx.TR_TWIST_BUTTONS
#                    | wx.TR_ROW_LINES
#                    | wx.TR_COLUMN_LINES
                    | wx.TR_FULL_ROW_HIGHLIGHT
                    )

        # Create items
        titlefont = wx.Font(16,
                            wx.FONTFAMILY_DEFAULT,
                            wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD,
                            )
        self.title = wx.StaticText(self, wx.ID_ANY,
                                   label="Accounts",
                                   size=(-1, -1),
                                   style=wx.ALIGN_CENTER,
                                   )
        self.title.SetFont(titlefont)

        self.tree = wx.TreeCtrl(self,
                                wx.ID_ANY,
                                style=tc_style,
                                )

        self.root = self.tree.AddRoot("Accounts")
#        self.tree.SetItemText(self.root, "col1 root")
        group1 = self.tree.AppendItem(self.root, "Group1")
        group2 = self.tree.AppendItem(self.root, "Group2")
        acct1 = self.tree.AppendItem(group1, "acct1")
        acct2 = self.tree.AppendItem(group1, "acct2")
        acct3 = self.tree.AppendItem(group2, "acct3")
        acct4 = self.tree.AppendItem(group2, "acct4")
#        self.tree.SetItemText(child, "col1")

#        self.tree.Expand(self.root)
        self.tree.ExpandAll()

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.title, 0, wx.EXPAND)
        self.vbox.Add((-1, 3), 0, wx.EXPAND)
        self.vbox.Add(self.tree, 1, wx.EXPAND)
        self.SetSizer(self.vbox)


class LedgerSummaryBar(wx.Panel):
    """ The legder summary bar """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent

        # TODO: Use decimal.Decimal types for balances
        self._online_bal = 0.0          # online balance
        self._avail_bal = 0.0           # online available balance
        self._curr_bal = 0.0            # current balance
        self._num_trans = 0             # number of transactions

        self._trans_fmt = "{:0>6} Transactions"
        self._trans_text = self._trans_fmt.format(self._num_trans)

        self._online_fmt = "Online Balance: ${:<8.2f}"
        self._online_text = self._online_fmt.format(self._online_bal)

        self._avail_fmt = "Avilable Balance: ${:<8.2f}"
        self._avail_text = self._avail_fmt.format(self._avail_bal)

        self._curr_fmt = "Current Balance: ${:<8.2f}"
        self._curr_text = self._curr_fmt.format(self._curr_bal)

        self._init_ui()

    def _init_ui(self):
        """ Initialize UI components """
        # Create various items
        # TODO: These displays can be instances of the same class
        self._num_trans_display = wx.StaticText(self, wx.ID_ANY,
                                                label=self._trans_text,
                                                size=(-1, -1),
                                                )

        self._online_display = wx.StaticText(self, wx.ID_ANY,
                                                 label=self._online_text,
                                                 size=(-1, -1),
                                                 )

        self._avail_display = wx.StaticText(self, wx.ID_ANY,
                                            label=self._avail_text,
                                            size=(-1, -1),
                                            )

        self._curr_display = wx.StaticText(self, wx.ID_ANY,
                                           label=self._curr_text,
                                           size=(-1, -1),
                                           )

        # Create layout managers and add items
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self._num_trans_display, 0, wx.EXPAND)
        self.hbox.Add((30, -1), 1, wx.EXPAND)
        self.hbox.Add(self._online_display, 0, wx.EXPAND)
        self.hbox.Add((30, -1), 0, wx.EXPAND)
        self.hbox.Add(self._avail_display, 0, wx.EXPAND)
        self.hbox.Add((30, -1), 0, wx.EXPAND)
        self.hbox.Add(self._curr_display, 0, wx.EXPAND)

        self.SetSizer(self.hbox)


    def _update(self):
        """ Updates the ledger summary """
        # query the database and calculate each
        pass

    @property
    def online_balance(self):
        """ Returns the online balance """
        return self._online_bal

    @online_balance.setter
    def online_balance(self, value):
        """ Sets the online balance """
        self._online_bal = value

    @property
    def num_transactions(self):
        """ Gets the number of transactions """
        return self._num_trans

    @num_transactions.setter
    def num_transactions(self, value):
        """ Sets the number of transactions """
        self._num_trans = value

    @property
    def available_balance(self):
        """ Gets the online available balance """
        return self._avail_bal

    @available_balance.setter
    def available_balance(self, value):
        """ Sets the online available balance """
        self._avail_bal = value

    @property
    def current_balance(self):
        """ Gets the current balance """
        return self._curr_bal

    @current_balance.setter
    def current_balance(self, value):
        """ Sets the current balance """
        self._curr_bal = value


class LedgerHeaderBar(wx.Panel):
    """ The ledger header bar """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent

        self._init_ui()

    def _init_ui(self):
        """ Initialize UI components """
        self.title_bar = wx.StaticText(self, wx.ID_ANY,
                                       "<placeholder for account name>",
                                       style=wx.ALIGN_CENTER,
                                       )

        vbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(self.title_bar, 1, wx.EXPAND)
        self.SetSizer(vbox)


# ---------------------------------------------------------------------------
### Run module as standalone
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    MainApp()
