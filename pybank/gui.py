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
### #------------------------------------------------------------------------
### Imports
### #------------------------------------------------------------------------
# Standard Library
import logging
import sys
import decimal
import os.path as osp

# Third Party
import wx
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
if __name__ == "__main__":
    sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
#from __init__ import VERSION
import pbsql

### #------------------------------------------------------------------------
### Module Constants
### #------------------------------------------------------------------------

LEDGER_COLOR_1 = wx.Colour(255, 255, 255, 255)
LEDGER_COLOR_2 = wx.Colour(255, 255, 204, 255)
DATABASE = "test_database.db"

### #------------------------------------------------------------------------
### Classes
### #------------------------------------------------------------------------

class MainApp(object):
    """ Main App """
    def __init__(self):
        self.app = wx.App()

        self.frame = MainFrame("PyBank", (1200, 800))

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
        self.mf_exit = wx.MenuItem(self.mfile, 103, "&Exit\tCtrl+Q",
                                   "Exit the application")

        # Add menu items to the menu
        self.mfile.Append(self.mf_new)
        self.mfile.Append(self.mf_open)
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
        print("on quit")
        self.Close(True)

    def _on_open(self, event):
        """ Open a file """
        print("on open")
        logging.info("Opening file")

    def _on_new(self, event):
        """ Create a new file """
        print("on new")
        logging.info("Creating new file")

    def _on_toggle_ledger_col(self, event):
        """ Toggles a ledger column on or off """
        col_num = event.Id - 30200      # Ledger columns are 0-indexed
                                        # but we always show the # col
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

#        p1 = SamplePanel(self, 'pink', "hafsdf")
        self.ledger_page = LedgerPanel(self)
        self.AddPage(self.ledger_page, "Ledger")

        p2 = SamplePanel(self, "green", "sdfdfsdfsdfsdfsd")
        self.AddPage(p2, "Other Stuff")

        p3 = SamplePanel(self, "sky blue", "sdfdfsdfsdfsdfsd")
        self.AddPage(p3, "Even more stuff")


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
        self.ledger = LedgerULC(self)
        self.summary_bar = LedgerSummaryBar(self)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.ledger, 1, wx.EXPAND)
        self.vbox.Add(self.summary_bar, 0, wx.EXPAND)
        self.SetSizer(self.vbox)


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
#        listmix.ListRowHighlighter.__init__(self, LEDGER_COLOR_1)

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
                self.SetItemBackgroundColour(row, LEDGER_COLOR_2)
            else:
                self.SetItemBackgroundColour(row, LEDGER_COLOR_1)

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
        print(num_items)

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
        print("Doubleclick on row: {}".format(row))
        self.change_row_to_edit(row)

    def change_row_to_edit(self, row):
        """ Modifies a row to edit-style. """
        print("modifying row {}".format(row))


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
        # Set style info for the FoldPanelBards (CaptionBars)
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
        pass


if __name__ == "__main__":
    MainApp()
