# -*- coding: utf-8 -*-
# pylint: disable=E1101, C0330, E0266
#   E1101 = Module X has no Y member
#   C0330 = Wrong continued indentation.
#   E0266 = too many leading '#' for block comment
"""
GUI Utilities that can be (or must be) stand-alone, such as password
promts and other dialogs.

Created on Tue May 12 13:21:37 2015

Usage:
    gui_utils.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""
# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
import logging
import time

# Third Party
import wx

# Package / Application
try:
    # Imports used by unit test runners
    from . import pbsql
    from . import plots
    from . import utils
    from . import crypto
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
#        from pybank import __init__ as __pybank_init
        from pybank import (__project_name__,
                            __version__,
                            )

        logging.debug("imports for Executable")

# ---------------------------------------------------------------------------
### Module Constants
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
### Classes
# ---------------------------------------------------------------------------
class PasswordPromptDialog(wx.Dialog):
    """ Dialog Box for user password. """
    def __init__(self, title="PyBank", prompt="Please enter your password:"):
        wx.Dialog.__init__(self, None, title=title)

        # Main Prompt
        label = wx.StaticText(self, -1, prompt)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        self.pw1 = wx.TextCtrl(self, size=(150, -1), style=wx.TE_PASSWORD)
        sizer.Add(self.pw1, 1, wx.ALIGN_CENTER|wx.ALL, 5)

        btnsizer = wx.StdDialogButtonSizer()

        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Center()


class PasswordCreateDialog(wx.Dialog):
    """ Dialog Box for creating a password. """
    def __init__(self):
        wx.Dialog.__init__(self, None, title="PyBank")

        # The prompt
        label = wx.StaticText(self, -1, "Please create a password:")

        # A vertical sizer to hold the two rows of prompt + grid
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        # 1st grid row: password label + entry box
        label = wx.StaticText(self, wx.ID_ANY, "Password:")
        self.pw1 = wx.TextCtrl(self, size=(-1, -1), style=wx.TE_PASSWORD)

        grid = wx.FlexGridSizer(2, 5, 0)
        alignment = wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT
        padding = wx.LEFT|wx.RIGHT
        grid.Add(label, 0, alignment|padding, 5)
        grid.Add(self.pw1, 1, wx.EXPAND|padding, 5)

        # 2st grid row: confirmation label + entry box
        label = wx.StaticText(self, wx.ID_ANY, "Confirm:", size=(-1, -1))
        self.pw2 = wx.TextCtrl(self, size=(-1, -1), style=wx.TE_PASSWORD)

        grid.Add(label, 0, alignment|padding, 5)
        grid.Add(self.pw2, 1, wx.EXPAND|padding, 5)

        grid.Fit(self)

        sizer.Add(grid, 0, wx.ALL, 5)

        # OK and Cancel buttons
        btnsizer = wx.StdDialogButtonSizer()

        self.ok_btn = wx.Button(self, wx.ID_OK)
        self.ok_btn.SetDefault()
        self.ok_btn.Disable()
        btnsizer.AddButton(self.ok_btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|padding|wx.BOTTOM, 5)

        self.Bind(wx.EVT_TEXT, self.on_txt_change, self.pw1)
        self.Bind(wx.EVT_TEXT, self.on_txt_change, self.pw2)

        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Center()

    def on_txt_change(self, event):
        """ Disable the "OK" button if the passwords don't match """
        pw1 = self.pw1.GetValue()
        pw2 = self.pw2.GetValue()
        if pw1 == pw2 and pw1 != '':
            self.ok_btn.Enable()
        else:
            self.ok_btn.Disable()


# ---------------------------------------------------------------------------
### Functions
# ---------------------------------------------------------------------------
def _prompt_pw(prompt=None):
    """ Internals to `prompt_pw` """
    app = wx.App()
    dialog = PasswordPromptDialog(prompt=prompt)
    # XXX: Is this a security risk? Sending an unencrypted
    #      password between functions and modules?
    if dialog.ShowModal() == wx.ID_OK:
        retval = dialog.pw1.GetValue()
    else:
        retval = None
    dialog.Destroy()
    app.MainLoop()
    return retval


def prompt_pw():
    """
    Prompt the user for a password.

    If the entered password incorrect, it loops until correct or the dialog
    is canceled. If canceled, returns False, else returns True.
    """
    # Password Prompt Loop
#    if not crypto.check_password_exists():
#        return

    prompt = "Please enter your password:"

    logging.debug('Starting password prompt loop')
    while True:
        password = _prompt_pw(prompt)
        if password is None:
            logging.debug('User canceled password prompt; exiting')
            return False
        elif crypto.check_password(password):
            logging.debug('Password OK')
            return True
        else:
            logging.debug('Invalid password')
            prompt = "Invalid password.\nPlease enter your password:"
            time.sleep(0.5)     # slow down brute-force attempts
            continue


def create_pw():
    """
    Have the user create a password.

    The same password must be entered on both lines.

    If canceled, returns False. Otherwise returns the password and saves
    it to the keyring.
    """
    app = wx.App()
    dialog = PasswordCreateDialog()
    # XXX: Is this a security risk? Sending an unencrypted
    #      password between functions and modules?
    if dialog.ShowModal() == wx.ID_OK:
        logging.debug("Creating password")
        crypto.create_password(dialog.pw1.GetValue())
        retval = True
    else:
        logging.debug("Canceled")
        retval = False
    dialog.Destroy()
    app.MainLoop()
    return retval


def change_pw():
    """
    Prompt the user to change the password.

    Returns True if the password was changed. False if canceled.
    """
    changed = False

    if prompt_pw():
        logging.debug("Password correct, moving to update")
        if create_pw():
            logging.debug("Password changed")
            changed = True

    return changed


if __name__ == "__main__":
    logging.info("Checking `prompt_pw`")
    prompt_pw()

    logging.info("Checking `create_pw`")
    create_pw()

    logging.info("Checking `change_pw`")
    change_pw()
