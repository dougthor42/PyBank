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

# Third Party
import wx
import wx.grid
import wx.lib.plot as wxplot
import numpy as np
#import wxmplot
#import wx.gizmos
import wx.lib.mixins.listctrl as listmix
#from wx.lib.splitter import MultiSplitterWindow
try:
    from agw import foldpanelbar as fpb
    from agw import ultimatelistctrl as ulc
except ImportError:
    import wx.lib.agw.foldpanelbar as fpb
    from wx.lib.agw import ultimatelistctrl as ulc
# Do I want to use wx? That's what I'm used to but it's not that well
# supported for python3...
# PyQt has more followers; Tkinter comes with python...
# Well, at the very least, I'll start off with wxPython since it's what I
# like the most and it's what I know the best.

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

        self.frame = MainFrame(TITLE_TEXT, (1200, 700))

        self.frame.Show()
        self.app.MainLoop()


class MainFrame(wx.Frame):
    """ Main Window of the PyBank program """
    def __init__(self, title, size):
        wx.Frame.__init__(self, None, wx.ID_ANY, title=title, size=size)
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
        self.mf_exit = wx.MenuItem(self.mfile, 103, "&Exit\tCtrl+Q",
                                   "Exit the application")

        # Add menu items to the menu
        self.mfile.Append(self.mf_new)
        self.mfile.Append(self.mf_open)
        self.mfile.Append(self.mf_close)
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

        # Edit Menu
#        self.Bind(wx.EVT_MENU, self._on_edit_menu1)

        # View Menu
#        self.Bind(wx.EVT_MENU, self._nothing)
        self.Bind(wx.EVT_MENU, self._on_toggle_ledger_col, id=30201, id2=30210)

        # Tools Menu

        # Options Menu

        # Help Menu

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


#%% Not used
class LedgerULC(ulc.UltimateListCtrl,
#                listmix.ColumnSorterMixin,
                listmix.ListCtrlAutoWidthMixin,
#                listmix.TextEditMixin,
#                listmix.ListRowHighlighter,    # not PY3 ready :-(
                ):
    """
    Main Ladger Widget.

    Inherits from ulc.UltimateListCtrl.

    See
    http://xoomer.virgilio.it/infinity77/AGW_Docs/ultimatelistctrl_module.html
    for docs.

    # TODO:
    -------
    [ ]     ColumnSorterMixin
    [ ]     AutoWidth for "Payee" column
    [x]     Show/Hide columns
    """
    def __init__(self, parent):
        self.parent = parent

        agw_style = (
                     wx.LC_REPORT
                     | wx.LC_VRULES
                     | wx.LC_HRULES
                     | wx.LC_SINGLE_SEL
                     | ulc.ULC_HAS_VARIABLE_ROW_HEIGHT
#                     | ulc.ULC_EDIT_LABELS
#                     | ulc.ULC_SINGLE_SEL
                     )

        # Initialize the parent
        ulc.UltimateListCtrl.__init__(self,
                                      parent,
                                      wx.ID_ANY,
                                      agwStyle=agw_style,
                                      )

        # Initialize mixins
#        listmix.TextEditMixin.__init__(self)
#        listmix.ListRowHighlighter.__init__(self, LEDGER_COLOR_ROW_ODD)

        # Create our columns and populate initial data.
        self._create_columns()
        self._populate_table()
        self._set_initial_hidden_states()
        self._add_edit_row()
#        self._init_sorting_mixin()

        # Auto-width mixin
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(5)         # Payee column
        self.resizeColumn(120)          # min width = 120px


        self._bind_events()

    # Used by ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        """
        Override Method for ColumnSorterMixin.

        See wx/lib/mixins/listctrl.py
        """
        return self

    def _create_columns(self):
        """
        Creates the columns for the ledger.
        """
        # (title, format, width)
        cols = [
                ("#", ulc.ULC_FORMAT_RIGHT, 30),
                ("Transaction Date", ulc.ULC_FORMAT_LEFT, 100),
                ("Date Entered", ulc.ULC_FORMAT_LEFT, 100),
                ("CheckNum", ulc.ULC_FORMAT_LEFT, 80),
                ("Payee", ulc.ULC_FORMAT_LEFT, 120),     # TODO: LIST_AUTOSIZE_FILL
                ("Downloaded Payee", ulc.ULC_FORMAT_LEFT, 120),
                ("Memo", ulc.ULC_FORMAT_LEFT, 150),
                ("Category", ulc.ULC_FORMAT_LEFT, 180),
                ("Label", ulc.ULC_FORMAT_LEFT, 160),
                ("Amount", ulc.ULC_FORMAT_RIGHT, 80),
                ("Balance", ulc.ULC_FORMAT_RIGHT, 80),
                ]

        for _i, (title, fmt, width) in enumerate(cols):
            self.InsertColumn(_i, title, fmt, width)

    def _populate_table(self):
        """ populates the list control directly from the v_ledger_0 view. """
        view = pbsql.LedgerView(DATABASE, "v_ledger_0")
        data = view.read_all()
        data = dict(enumerate(data))
        starting_bal = decimal.Decimal(200)
        balance = starting_bal

        for _i in range(len(data)):
            # Create the row
            row = self.InsertStringItem(_i, str(_i + 1))

            # Then set the background color
            if _i % 2 == 0:
                self.SetItemBackgroundColour(row, LEDGER_COLOR_ROW_EVEN)
            else:
                self.SetItemBackgroundColour(row, LEDGER_COLOR_ROW_ODD)

            # Accumulate the account value
            # TODO: get rid of this hack
            balance += decimal.Decimal(data[_i][-1])
            temp_data = list(data[_i])
            temp_data.append(balance)
            data[_i] = tuple(temp_data)

            # Add the data
            for _col, item in enumerate(data[_i]):
                val = '' if item is None else str(item)
                if _col == 6 or _col == 7:
                    cb = wx.ComboBox(self,
                                     wx.ID_ANY,
                                     value=val,
                                     choices=['a', 'b', 'c'],
                                     )
                    self.SetItemWindow(row, _col + 1, cb, expand=True)
                else:
                    self.SetStringItem(row, _col + 1, val)

    def _set_initial_hidden_states(self):
        """
        Sets the initial hidden states for the columns based on the View Menu.

        """
        # TODO: Move column states to a config file so that it can persist
        #       Also means I don't have to access the menu value for
        #       hidden/shown - I can just access the variable that was set
        #       by reading the config file.

        # XXX: For now, just hard-code the defaults 2 and 6
        self.SetColumnShown(2, False)
        self.SetColumnShown(6, False)

    def _add_edit_row(self):
        """
        Adds an edit row to the end of the Ledger so that users can add
        items.
        """
        num_items = self.GetItemCount()
        logging.debug(num_items)

        row = self.InsertStringItem(num_items, "")
        for _col in range(1, self.GetColumnCount()):
            if _col == 7 or _col == 8:
                cb = wx.ComboBox(self,
                                 wx.ID_ANY,
                                 value='',
                                 choices=['a', 'b', 'c'],
                                 )
                self.SetItemWindow(row, _col, cb, expand=True)
            elif _col == 10:
                # don't allow the user to add a new balance
                continue
            else:
                tc = wx.TextCtrl(self,
                                 wx.ID_ANY,
                                 value='',
                                 )
                self.SetItemWindow(row, _col, tc, expand=True)

    def _init_sorting_mixin(self):
        """ must be called after list exists """
        listmix.ColumnSorterMixin.__init__(self, 9)

    def _bind_events(self):
        """ Bind all the events """
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_item_doubleclick)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_item_select)

    def _on_column_click(self, event):
        """
        Fire on column click
        """
        self.Refresh()
        event.Skip()

    def _on_item_select(self, event):
        """ Highlight the entire row when a single item is selected """
        pass

    def _on_item_doubleclick(self, event):
        """
        Change the cell to editable.
        """
        row = event.GetIndex()
        logging.debug("Doubleclick on row: {}".format(row))
        self.change_row_to_edit(row)

    def change_row_to_edit(self, row):
        """ Modifies a row to edit-style. """
        logging.debug("modifying row {}".format(row))

#%% Not used
class LedgerVirtual(wx.ListCtrl,
#                    listmix.ColumnSorterMixin,
                    listmix.ListCtrlAutoWidthMixin,
#                    listmix.TextEditMixin,
#                    listmix.ListRowHighlighter,    # not PY3 ready :-(
                ):
    """
    Main Ladger Widget.

    Inherits from ulc.UltimateListCtrl.

    See
    http://xoomer.virgilio.it/infinity77/AGW_Docs/ultimatelistctrl_module.html
    for docs.

    # TODO:
    -------
    [ ]     ColumnSorterMixin
    [ ]     AutoWidth for "Payee" column
    [x]     Show/Hide columns
    """
    def __init__(self, parent):
        self.parent = parent

        agw_style = (
                     wx.LC_REPORT
                     | wx.LC_VRULES
                     | wx.LC_HRULES
                     | wx.LC_SINGLE_SEL
                     | wx.LC_VIRTUAL
                     )

        # Initialize the parent
        wx.ListCtrl.__init__(self,
                                      parent,
                                      wx.ID_ANY,
                                      style=agw_style,
                                      )

        view = pbsql.LedgerView(DATABASE, "v_ledger_0")
        data = view.read_all()
        num_items = len(data)
        self.SetItemCount(num_items)
        self.data_source = dict(enumerate(data))

        # Initialize mixins
#        listmix.TextEditMixin.__init__(self)
#        listmix.ListRowHighlighter.__init__(self, LEDGER_COLOR_ROW_ODD)

        # Create our columns and populate initial data.
        self._create_columns()
#        self._populate_table()
#        self._set_initial_hidden_states()
#        self._add_edit_row()
#        self._init_sorting_mixin()

        # Auto-width mixin
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(5)         # Payee column
        self.resizeColumn(120)          # min width = 120px


        self._bind_events()

    # -----------------------------------------------------------------------
    ### Method Overrides
    # -----------------------------------------------------------------------

    # Used by ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        """
        Override Method for ColumnSorterMixin.

        See wx/lib/mixins/listctrl.py
        """
        return self

    def OnGetItemText(self, item, column):
        data = self.data_source[item]
        return data[column]

    def OnGetItemAttr(self, item):
        return None

    def OnGetItemImage(self, item):
        return -1

    # -----------------------------------------------------------------------
    ### Private Methods
    # -----------------------------------------------------------------------

    def _create_columns(self):
        """
        Creates the columns for the ledger.
        """
        # (title, format, width)
        cols = [
                ("#", ulc.ULC_FORMAT_RIGHT, 30),
                ("Transaction Date", ulc.ULC_FORMAT_LEFT, 100),
                ("Date Entered", ulc.ULC_FORMAT_LEFT, 100),
                ("CheckNum", ulc.ULC_FORMAT_LEFT, 80),
                ("Payee", ulc.ULC_FORMAT_LEFT, 120),     # TODO: LIST_AUTOSIZE_FILL
                ("Downloaded Payee", ulc.ULC_FORMAT_LEFT, 120),
                ("Memo", ulc.ULC_FORMAT_LEFT, 150),
                ("Category", ulc.ULC_FORMAT_LEFT, 180),
                ("Label", ulc.ULC_FORMAT_LEFT, 160),
                ("Amount", ulc.ULC_FORMAT_RIGHT, 80),
                ("Balance", ulc.ULC_FORMAT_RIGHT, 80),
                ]

        for _i, (title, fmt, width) in enumerate(cols):
            self.InsertColumn(_i, title, fmt, width)

    def _populate_table(self):
        """ populates the list control directly from the v_ledger_0 view. """
        view = pbsql.LedgerView(DATABASE, "v_ledger_0")
        data = view.read_all()
        data = dict(enumerate(data))
        starting_bal = decimal.Decimal(200)
        balance = starting_bal

        for _i in range(len(data)):
            # Create the row
            row = self.InsertStringItem(_i, str(_i + 1))

            # Then set the background color
            if _i % 2 == 0:
                self.SetItemBackgroundColour(row, LEDGER_COLOR_ROW_EVEN)
            else:
                self.SetItemBackgroundColour(row, LEDGER_COLOR_ROW_ODD)

            # Accumulate the account value
            # TODO: get rid of this hack
            balance += decimal.Decimal(data[_i][-1])
            temp_data = list(data[_i])
            temp_data.append(balance)
            data[_i] = tuple(temp_data)

            # Add the data
            for _col, item in enumerate(data[_i]):
                val = '' if item is None else str(item)
                if _col == 6 or _col == 7:
                    cb = wx.ComboBox(self,
                                     wx.ID_ANY,
                                     value=val,
                                     choices=['a', 'b', 'c'],
                                     )
                    self.SetItemWindow(row, _col + 1, cb, expand=True)
                else:
                    self.SetStringItem(row, _col + 1, val)

    def _set_initial_hidden_states(self):
        """
        Sets the initial hidden states for the columns based on the View Menu.

        """
        # TODO: Move column states to a config file so that it can persist
        #       Also means I don't have to access the menu value for
        #       hidden/shown - I can just access the variable that was set
        #       by reading the config file.

        # XXX: For now, just hard-code the defaults 2 and 6
        self.SetColumnShown(2, False)
        self.SetColumnShown(6, False)

    def _add_edit_row(self):
        """
        Adds an edit row to the end of the Ledger so that users can add
        items.
        """
        num_items = self.GetItemCount()
        logging.debug(num_items)

        row = self.InsertStringItem(num_items, "")
        for _col in range(1, self.GetColumnCount()):
            if _col == 7 or _col == 8:
                cb = wx.ComboBox(self,
                                 wx.ID_ANY,
                                 value='',
                                 choices=['a', 'b', 'c'],
                                 )
                self.SetItemWindow(row, _col, cb, expand=True)
            elif _col == 10:
                # don't allow the user to add a new balance
                continue
            else:
                tc = wx.TextCtrl(self,
                                 wx.ID_ANY,
                                 value='',
                                 )
                self.SetItemWindow(row, _col, tc, expand=True)

    def _init_sorting_mixin(self):
        """ must be called after list exists """
        listmix.ColumnSorterMixin.__init__(self, 9)

    def _bind_events(self):
        """ Bind all the events """
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_item_doubleclick)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_item_select)

    def _on_column_click(self, event):
        """
        Fire on column click
        """
        self.Refresh()
        event.Skip()

    def _on_item_select(self, event):
        """ Highlight the entire row when a single item is selected """
        pass

    def _on_item_doubleclick(self, event):
        """
        Change the cell to editable.
        """
        row = event.GetIndex()
        logging.debug("Doubleclick on row: {}".format(row))
        self.change_row_to_edit(row)

    def change_row_to_edit(self, row):
        """ Modifies a row to edit-style. """
        logging.debug("modifying row {}".format(row))

#%% Good
class LedgerGridBaseTable(wx.grid.GridTableBase):
    """
    """
    def __init__(self, parent):
        wx.grid.GridTableBase.__init__(self)
        self.parent = parent
        self.column_labels, self.col_types = self._set_columns()
        self.data = [[]]

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

    def GetValue(self, row, column):
        """
        Get the cell value from the data or database.

        Override Method

        Is called on every cell at init and then again when cells are
        clicked.
        """
#        logging.debug("Getting value of r{}c{}".format(row, column))
        try:
            value = self.data[row][column]
            if value is None or value == 'None':
                return ''
            else:
                return value
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        """
        Sets the value of a cell.

        Override Method.
        """
        self._set_value(row, col, value)

    def _set_value(self, row, col, value):
        """
        Updates the database with the value of the cell.

        # TODO: If updating an existing payee name, then we
        #       add to the display_name table.
        #       If adding a new payee name, check it against the payee table
        #       Add if needed, otherwise...?
        """
        logging.debug("Setting r{}c{} to `{}`".format(row, col, value))
        try:
            # update database entry
            # gotta get the tid and send *that* to the update method
            # to account for deleted entries.
            tid = self.data[row][0]
            self.ledger_view.update_transaction(tid, col, value)
        except IndexError:
            # add a new row
            logging.debug("Adding a new row")
            self.ledger_view.insert_row()
            self._update_data()         # Must come before _set_value()
            self._set_value(row, col, value)

            # tell grid we've added a row
            action = wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED
            msg = wx.grid.GridTableMessage(self, action, 1)
            self.GetView().ProcessTableMessage(msg)
            self.parent._format_table()
        else:
            # run this if no errors
            self._update_data()
            # _update_data() does not update the balance for all rows. hmm...
            # Update values
            action = wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES
            msg = wx.grid.GridTableMessage(self, action)
            self.GetView().ProcessTableMessage(msg)
            self.parent._format_table()

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
        # (title, type, width)
        # TODO: make column order depend only on the DB view
        cols = [
                ("tid",                 wx.grid.GRID_VALUE_STRING, 30),
                ("Date",                wx.grid.GRID_VALUE_TEXT, 100),
                ("Date Entered",        wx.grid.GRID_VALUE_TEXT, 100),
                ("CheckNum",            wx.grid.GRID_VALUE_TEXT, 80),
                ("Payee",               wx.grid.GRID_VALUE_TEXT, 120),
                ("Downloaded Payee",    wx.grid.GRID_VALUE_TEXT, 120),
                ("Memo",                wx.grid.GRID_VALUE_TEXT, 150),
                ("Category",            wx.grid.GRID_VALUE_TEXT, 180),
                ("Label",               wx.grid.GRID_VALUE_TEXT, 160),
                ("Amount",              wx.grid.GRID_VALUE_TEXT, 80),
                ("Balance",             wx.grid.GRID_VALUE_TEXT, 80),
                ]

        labels = [_i[0] for _i in cols]
        types = [_i[1] for _i in cols]

        for _i, title in enumerate(labels):
            self.SetColLabelValue(_i, title)

        return (labels, types)

#    def _update_data(self):
#        # grab the table data from the database
#        self.ledger_view = pbsql.LedgerView(DATABASE, 0)
#        data = self.ledger_view.read_all()
#
#        # calculate the running balance and add it to the data
#        starting_bal = decimal.Decimal(200)
#        balance = starting_bal
#        data = list([list(str(_x) for _x in row) for row in data])
#        self.data = []
#        for row in data:
#            balance += decimal.Decimal(row[-1])
#            row[-2] = str(row[-2])
#            row.append(str(balance))
#            self.data.append(row)

    def _update_data(self):
        # grad the table data from the database
        # need to somehow grab the session from... somewhere.
        data = sa_orm_transactions.query_view()

        # calculate the running balance and add it to the data
        starting_bal = decimal.Decimal(200)
        balance = starting_bal
        data = list([list(str(_x) for _x in row) for row in data])
        self.data = []
        for row in data:
            balance += decimal.Decimal(row[-1])
            row[-2] = str(row[-2])
            row.append(str(balance))
            self.data.append(row)

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
            if column in (2, 8, 9):
                attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
            else:
                attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER)
            self.SetColAttr(column, attr)

    def _color_dollars(self):
        """ Colors negative amounts and balances as red """
        logging.debug("Coloring negative balances")
        num_rows = self.GetNumberRows() - 1
        for row in range(num_rows):
            for col in (8, 9):
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
