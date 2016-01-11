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
    from . import (__project_name__,
                   __version__,
                   )
#    from . import plots
    from . import utils
    from . import crypto
    from . import gui_utils
    from . import orm
    logging.debug("Imports for gui.py complete (Method: UnitTest)")
except SystemError:
    try:
        # Imports used by Spyder
        from __init__ import (__project_name__,
                              __version__,
                              )
#        import plots
        import utils
        import crypto
        import gui_utils
        import orm
        logging.debug("Imports for gui.py complete (Method: Spyder IDE)")
    except ImportError:
         # Imports used by cx_freeze
        from pybank import (__project_name__,
                            __version__,
                            )
#        from pybank import plots
        from pybank import utils
        from pybank import crypto
        from pybank import gui_utils
        from pybank import orm
        logging.debug("Imports for gui.py complete (Method: Executable)")


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

        # Having the GridCellChoiceEditor seems to cause a wxAssertionError
        # but doens't appear to do anything bad, so I'm just handling it here
        # because it's annoying.
        try:
            self.app.MainLoop()
        except wx.wxAssertionError:
            pass


class MainFrame(wx.Frame):
    """ Main Window of the PyBank program """
    def __init__(self, title, size):
        wx.Frame.__init__(self, None, wx.ID_ANY, title=title, size=size)

        # Set up some timers for backup and write-to-db
#        self.write_db_timer = wx.Timer(self)
#        self.write_db_timer.Start(1000)
#        logging.debug("Write-to-database timer started")

        self.encryption_timer = wx.Timer(self)
        self.encryption_timer.Start(5 * 60 * 1000)      # Every 5 minutes
        logging.info("Encryption timer started")

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
#        self.Bind(wx.EVT_TIMER, self._on_write_db_timer , self.write_db_timer)

        # Other
        self.Bind(wx.EVT_CLOSE, self._on_close_event, self)

    def _on_close_event(self, event):
        """
        Catch all of the close events, including those from the window
        manager (such as the upper-right "X" button and Alt-F4) as well
        as the close events that my program sends like from self._on_quit().

        This will handle things like saving any remaining changes, backing
        up data, and confirming close.
        """
        logging.debug("close event fired!")


        # Get the required encryption stuff
        key = crypto.get_key()

        # dump the memory database directly to an encrypted file.
        dump = orm.sqlite_iterdump(orm.engine, orm.session)
        dump = "".join(line for line in dump)
        dump = dump.encode('utf-8')

        new_file = "test_database.pybank"
        crypto.encrypted_write(new_file, key, dump)

        self.Destroy()

    def _on_quit(self, event):
        """ Execute quit actions """
        logging.debug("on quit")
        self.Close(force=True)

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
        logging.error("(Not yet implemented)")

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
        logging.info("Encryption Timer event start")

        # Get the required encryption stuff
        key = crypto.get_key()

        # dump the memory database directly to an encrypted file.
        dump = orm.sqlite_iterdump(orm.engine, orm.session)
        dump = "".join(line for line in dump)
        dump = dump.encode('utf-8')

        new_file = "test_database.pybank"
        crypto.encrypted_write(new_file, key, dump)

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
        self.summary_bar._update()

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.header_bar, 0, wx.EXPAND)
        self.vbox.Add(self.ledger, 1, wx.EXPAND)
        self.vbox.Add(self.summary_bar, 0, wx.EXPAND)
        self.SetSizer(self.vbox)


class LedgerGridBaseTable(wx.grid.GridTableBase):
    """
    """
    columns = utils.LedgerCols

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

        self.cat_data = [(row.category_id, row.name, row.parent)
                          for row in orm.query_category()]
        choiceList = []
        for row in self.cat_data:
            pk = row[0]
            choiceList.append(utils.build_category_string(pk, self.cat_data))
        self.choiceList = choiceList

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
        return str(self._get_value(row, col))

    def _get_value(self, row, col):
        """
        Private logic for the GetValue() override method.
        """
#        logging.debug("Getting value of r{}c{}".format(row, column))
        try:
            value = self.data[row][col]
        except IndexError:
            return ''

        if col == self.columns.category.index:
            try:
                return utils.build_category_string(value, self.cat_data)
            except TypeError:
                return ''

        if value is None or value == 'None':
            return ''
        else:
            return str(value)

    def SetValue(self, row, col, value):
        """
        Sets the value of a cell.

        Override Method.
        """
        self._set_value(row, col, value)

    # for SQLAlchemy backend
    def _set_value(self, row, col, value):
        """
        Updates the data value for a given cell.

        Does not attempt to update the database
        """
        logging.info("Setting r{}c{} to `{}`".format(row, col, value))
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
        labels = [_i.col_name for _i in self.columns]
        types = [_i.col_type for _i in self.columns]

        for _i, title in enumerate(labels):
            self.SetColLabelValue(_i, title)

        return (labels, types)

#    def _calc_balance(self):
#        balance = decimal.Decimal('200')        # Starting balance
#
#
#        for row in self.data:
#            balance += decimal.Decimal(row[-2])
#            row[-1


    @utils.logged
    def _update_data(self):
        # grab the table data from the database
        self.data = []

        # convert the query results to something usable by the grid
        # Also calculate the running balancefor the view.
        # TODO: I hate this - come up with an alternate solution
        starting_bal = decimal.Decimal(200)
        balance = starting_bal
        for row_num, row_data in enumerate(orm.query_ledger_view()):
            data_dict = row_data.__dict__
            row_values = []
            for item in self.columns:
                if item.view_name is None:
                    continue

                row_values.append(data_dict[item.view_name])

            balance += decimal.Decimal(row_values[-1])
            row_values[-1] = str(row_values[-1])
            row_values.append(str(balance))
            self.data.append(row_values)

#        print(list(x for x, _, _, _ in self.columns))
#        for row in data:
#            print(row)

        # update the summary bar. Need to go to the grandparent.
        try:
            self.parent.parent.summary_bar._update()
        except AttributeError:
            # on initialization, the summary_bar object hasn't been created
            # yet so we just ignore the error. LedgerPanel._init_ui() takes
            # care of updating the summary_bar
            pass


class LedgerGrid(wx.grid.Grid):
    """
    """
    def __init__(self, parent):
        logging.info("Initializing LedgerGrid")
        wx.grid.Grid.__init__(self, parent, wx.ID_ANY)

        self.parent = parent
        self._setup()

        choiceEditor = wx.grid.GridCellChoiceEditor(self.table.choiceList,
                                                    allowOthers=True)

        for row in range(self.GetNumberRows()):
            self.SetCellEditor(row, 7, choiceEditor)

    @utils.logged
    def _setup(self):
        logging.info("Running LedgerGrid._setup()")
        self.table = LedgerGridBaseTable(self)

        self.SetTable(self.table, takeOwnership=True)

        self.SetRowLabelSize(30)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(True)

        self._bind_events()

        self._format_table()

    @utils.logged
    def _bind_events(self):
        logging.info("Binding events for LedgerGrid")
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK,
                  self._on_left_dclick,
                  self)

        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK,
                  self._on_right_click,
                  self)

        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK,
                  self._on_left_click,
                  self)

        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED,
                  self._on_grid_cell_changed,
                  self)

        self.Bind(wx.grid.EVT_GRID_CELL_CHANGING,
                  self._on_grid_cell_changing,
                  self)

    @utils.logged
    def _format_table(self):
        """ Formats all table properties """
        logging.info("Formatting table")
        self._color_rows()
        self._align_columns()
        self._color_dollars()

    @utils.logged
    def _color_rows(self):
        """ Color alternating rows and color the last row light grey """
        logging.info("Coloring rows")
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
        logging.info("Setting column alignment")
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
        logging.info("Coloring negative balances")
        num_rows = self.GetNumberRows() - 1
        for row in range(num_rows):
            for col in (9, 10):
                try:
                    val = float(self.GetCellValue(row, col))
                except ValueError:
                    logging.warning("Unable to convert r%sc%s to float. Assuming 0 for row coloring.", row, col)
                    val = 0
                if val < 0:
                    self.SetCellTextColour(row, col,
                                           LEDGER_COLOR_VALUE_NEGATIVE)
                else:
                    self.SetCellTextColour(row, col,
                                           LEDGER_COLOR_VALUE_POSITIVE)


    def _on_left_dclick(self, event):
        # TODO: get cell coord from event
        rc = (event.GetRow(), event.GetCol())
        logging.debug("double left click on cell {}".format(rc))
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

    def _on_right_click(self, event):
        rc = (event.GetRow(), event.GetCol())
        logging.debug("right-click detected on cell {}".format(rc))

    def _on_left_click(self, event):
        """
        Fires when a left-click happens.

        1.  Record the current cursor position
        2.  Move the grid cursor to the new cell (default behavior of this
            event)
        3.  If there is modified data, attempt to add it to the database.

        """
        logging.debug("Left-click detected")
        previous_rc = (self.GetGridCursorRow(), self.GetGridCursorCol())
        new_rc = (event.GetRow(), event.GetCol())

        # Don't do anything if we haven't moved grid location
        if previous_rc == new_rc:
            logging.debug("Cursor didn't move.")
            return

        self.SetGridCursor(*new_rc)

        logging.debug("previous_rc = {}".format(previous_rc))
        logging.debug("new_rc = {}".format(new_rc))

        if self.table.data_is_modified and new_rc[0] != previous_rc[0]:
            # TODO: Fill this out
            try:
                logging.info("Attempting to write data to database")
                orm.insert_ledger(acct=1,
                                  date=None,
                                  enter_date=None,
                                  check_num=None,
                                  amount="123.4",
                                  payee=None,
                                  category=None,
                                  label=None,
                                  memo=None,
                                  fitid=-1,
                                  )
            except TypeError:
                logging.exception("Error writing to database!", stack_info=True)
            else:
                logging.info("DB write successful.")
                logging.debug(orm.session.new)
                logging.debug(orm.session.dirty)
                orm.session.commit()
                self.parent.summary_bar._update()
                self.table.data_is_modified = False


    def _on_grid_cell_changed(self, event):
        """ Fires after a cell's data has changed. """
        logging.debug("grid cell changed")
        logging.debug("{}".format(event))

    def _on_grid_cell_changing(self, event):
        """ Fires before a cell's data is changed. Can be vetoed. """
        logging.debug("grid cell about to change")
        logging.debug("{}".format(event))

        if event.GetCol() == 3:         # CheckNum column
            try:
                int(event.GetString())
            except ValueError:
                log_msg = "Unable to cast '{}' to int. Reverting."
                logging.warning(log_msg.format(event.GetString()))
                event.Veto()
        elif event.GetCol() == 10:      # Blanace Column
            logging.warning("Can't change the 'Balance' column")
            event.Veto()
        elif event.GetCol() == 9:       # Amount Column
            try:
                decimal.Decimal(event.GetString())
            except decimal.InvalidOperation:
                log_msg = "Unable to cast '{}' to type `Decimal`. Reverting."
                logging.warning(log_msg.format(event.GetString()))
                event.Veto()
        else:
            pass


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
        self._online_bal = decimal.Decimal("0.00")  # online balance
        self._avail_bal = decimal.Decimal("0.00")   # online available balance
        self._curr_bal = decimal.Decimal("0.00")    # current balance
        self._num_trans = 0                         # number of transactions

            # can't fill with spaces because the text isn't fixed width and
            # I haven't set the wx.StaticText object to be fixed width.
        self._trans_fmt = "{:0>6} Transactions"
        self._trans_text = self._trans_fmt.format(self._num_trans)

        self._online_fmt = "Online Balance: {:<16s}"
        self._online_text = self._online_fmt.format(utils.moneyfmt(self._online_bal))

        self._avail_fmt = "Avilable Balance: {:<16s}"
        self._avail_text = self._avail_fmt.format(utils.moneyfmt(self._avail_bal))

        self._curr_fmt = "Current Balance: {:<16s}"
        self._curr_text = self._curr_fmt.format(utils.moneyfmt(self._curr_bal))

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

    @utils.logged
    def _update(self):
        """ Updates the ledger summary """
        logging.info("updating summary bar")
        data = self.parent.ledger.table.data    # Should I not do this because
                                                # of memory usage?

        self.online_balance = decimal.Decimal('0.00')
        self.num_transactions = len(data)
        self.available_balance = decimal.Decimal('0.00')
        self.current_balance = decimal.Decimal(data[-1][-1])

    @property
    def online_balance(self):
        """ Returns the online balance """
        return self._online_bal

    @online_balance.setter
    def online_balance(self, value):
        """ Sets the online balance """
        self._online_bal = value
        self._online_text = self._online_fmt.format(utils.moneyfmt(value))
        self._online_display.SetLabel(self._online_text)

    @property
    def num_transactions(self):
        """ Gets the number of transactions """
        return self._num_trans

    @num_transactions.setter
    def num_transactions(self, value):
        """ Sets the number of transactions """
        self._num_trans = value
        self._trans_text = self._trans_fmt.format(value)
        self._num_trans_display.SetLabel(self._trans_text)

    @property
    def available_balance(self):
        """ Gets the online available balance """
        return self._avail_bal

    @available_balance.setter
    def available_balance(self, value):
        """ Sets the online available balance """
        self._avail_bal = value
        self._avail_text = self._avail_fmt.format(utils.moneyfmt(value))
        self._avail_display.SetLabel(self._avail_text)

    @property
    def current_balance(self):
        """ Gets the current balance """
        return self._curr_bal

    @current_balance.setter
    def current_balance(self, value):
        """ Sets the current balance """
        self._curr_bal = value
        self._curr_text = self._curr_fmt.format(utils.moneyfmt(value))
        self._curr_display.SetLabel(self._curr_text)


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
