# -*- coding: utf-8 -*-
# pylint: disable=E1101
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
# Standard Library
import logging
import sys
import os.path as osp

# Third Party
import wx
from wx.lib.splitter import MultiSplitterWindow
try:
    from agw import foldpanelbar as fpb
except ImportError:
    import wx.lib.agw.foldpanelbar as fpb
# Do I want to use wx? That's what I'm used to but it's not that well
# supported for python3...
# PyQt has more followers; Tkinter comes with python...
# Well, at the very least, I'll start off with wxPython since it's what I
# like the most and it's what I know the best.

# Package / Application
if __name__ == "__main__":
    sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
#from __init__ import VERSION


class MainApp(object):
    """ Main App """
    def __init__(self):
        self.app = wx.App()

        self.frame = MainFrame("PyBank", (800, 600))

        self.frame.Show()
        self.app.MainLoop()


class MainFrame(wx.Frame):
    """ Main Window of the PyBank program """
    def __init__(self, title, size):
        wx.Frame.__init__(self, None, wx.ID_ANY, title=title, size=size)
        self._init_ui()

    def _init_ui(self):
        """ Initi UI Components """
        # Create the menu bar
        self.menu_bar = wx.MenuBar()

        self._create_menus()
        self._create_menu_items()
        self._add_menu_items()
        self._add_menus()
        self._bind_events()

        # Initialize default states


        # Set the MenuBar and create a status bar
        self.SetMenuBar(self.menu_bar)
        self.CreateStatusBar()

        self.panel = MainPanel(self)       # for now.

    def _create_menus(self):
        """ Create each menu for the menu bar """
        # TODO: Switch to wx.RibbonBar? It looks pretty nice.
        self.mfile = wx.Menu()
        self.medit = wx.Menu()
        self.mview = wx.Menu()
        self.mtools = wx.Menu()
        self.mopts = wx.Menu()
        self.mhelp = wx.Menu()

    def _create_menu_items(self):
        """ Create each menu item """
        self.mf_exit = wx.MenuItem(self.mfile,
                                   wx.ID_ANY,
                                   "&Exit\tCtrl+Q",
                                   "Exit the application",
                                   )

        self.mf_open = wx.MenuItem(self.mfile,
                                   wx.ID_ANY,
                                   "&Open\tCtrl+O",
                                   "Open a PyBank file",
                                   )


        self.mf_new = wx.MenuItem(self.mfile,
                                  wx.ID_ANY,
                                  "&New\tCtrl+N",
                                  "Create a new PyBank file",
                                  )

    def _add_menu_items(self):
        """ Add each menu item to the respective menu """
        self.mfile.Append(self.mf_new)
        self.mfile.Append(self.mf_open)
        self.mfile.AppendSeparator()
        self.mfile.Append(self.mf_exit)

    def _add_menus(self):
        """ Add the fully-formed menus to the menu bar """
        self.menu_bar.Append(self.mfile, "&File")
        self.menu_bar.Append(self.medit, "&Edit")
        self.menu_bar.Append(self.mview, "&View")
        self.menu_bar.Append(self.mtools, "&Tools")
        self.menu_bar.Append(self.mhelp, "&Help")

    def _bind_events(self):
        """ Bind all initial events """
        self.Bind(wx.EVT_MENU, self._on_quit, self.mf_exit)
        self.Bind(wx.EVT_MENU, self._on_open, self.mf_open)
        self.Bind(wx.EVT_MENU, self._on_new, self.mf_new)

    def _on_quit(self, event):
        """ Execute quit actions """
        self.Close(True)

    def _on_open(self, event):
        """ Open a file """
        logging.info("Opening file")

    def _on_new(self, event):
        """ Create a new file """
        logging.info("Creating new file")


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

        self.p1 = AccountList(self.splitter)
        self.p2 = MainNotebook(self.splitter)

        # Set up the splitter attributes
        self.splitter.SetMinimumPaneSize(100)
        self.splitter.SplitVertically(self.p1, self.p2, 200)

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
        wx.StaticText(self, -1, label, (5,5))


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
        p1 = Ledger(self)
        self.AddPage(p1, "Ledger")

        p2 = SamplePanel(self, "green", "sdfdfsdfsdfsdfsd")
        self.AddPage(p2, "Other Stuff")

        p3 = SamplePanel(self, "sky blue", "sdfdfsdfsdfsdfsd")
        self.AddPage(p3, "Even more stuff")


class Ledger(wx.Panel):
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
        self.ledger = wx.ListCtrl(self, wx.ID_ANY,
#                                  size=(300, 300),
#                                  style=wx.LC_VIRTUAL,
                                  style=wx.LC_REPORT #| wx.LC_VIRTUAL,
                                  )

        self.ledger.AppendColumn("Date")
#        self.ledger.AppendColumn("Entered Date")
        self.ledger.AppendColumn("CheckNum")
        self.ledger.AppendColumn("Payee")
        self.ledger.AppendColumn("Downloaded Payee")
        self.ledger.AppendColumn("Memo")
        self.ledger.AppendColumn("Category")
        self.ledger.AppendColumn("Label")
        self.ledger.AppendColumn("Amount")
        self.ledger.AppendColumn("Balance")

        item1 = wx.ListItem().SetData(1)
        item2 = wx.ListItem().SetData(2)

        self.ledger.InsertItem(1, "string")
        self.ledger.InsertItem(2, "item2")

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.ledger, 1, wx.EXPAND)
        self.SetSizer(self.hbox)


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
        self._online_bal = 0.0            # online balance
        self._avail_bal = 0.0      # online available balance
        self._curr_bal = 0.0              # current balance
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
        self.hbox.Add((-1, -1), 1, wx.EXPAND)
        self.hbox.Add(self._online_display, 0, wx.EXPAND)
        self.hbox.Add((-1, -1), 1, wx.EXPAND)
        self.hbox.Add(self._avail_display, 0, wx.EXPAND)
        self.hbox.Add((-1, -1), 1, wx.EXPAND)
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
