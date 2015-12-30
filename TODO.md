# Pybank TODO List

## Contents:
1. [Example](#things)
1.

## Things:
+ [ ] Need to make sure that when the program crashes, the SQLite db file
      is still encrypted.
      + Accomplished by having an in-memory database which is then dumped
        directly to an encrypted file periodically.
      + If the program crashes, then the in-memory database should fall off
        the face of the earth during a garbage collect.
+ [ ] Update source code with my current best practices.
+ [ ] Add option to export data as csv.
+ [ ] Get ofx import working
+ [ ] ~~Once PySQLCypher gets to Python3, switch to that~~
      + Actually, not really. I like my solution of saving the encrypted txt.
+ [ ] Create config file for varoius options
+ [ ] Create options screen
      + Auto-save frequency
      + Decimal localization
      + Show thousands separator True/False
+ [ ] Look into alternate pepper solution
      + perhaps unique to the computer it's running on? But what if the
        user wants to change computers...
      + secondary password?
+ [ ] Scurity Review!
+ [ ] Switch to wx.RibbonBar?
+ [ ] Auto-populate View -> Ledger Columns menu from the table.
+ [ ] Refactor gui.MainFrame._on_encryption_timer() method
+ [ ] I have a note in gui.MainNotebook._change_to_plots() to change it from
      pulling data from the ledger to pulling data directly from the database
      for some reason... /shrug.
+ [ ] In general, get the plots working
+ [ ] Add options to change plot range
+ [ ] Add support for multiple accounts
+ [ ] Move ledger balance and amount to numpy arrays?
+ [ ] Refactor gui.LedgerGridBaseTable._get_value(). I hate it.
+ [ ] Refactor gui.LedgerGridBaseTable._update_data()
+ [ ] Make it so that data is only written to the in-memory database when
      the user moves their cursor to a different line.
      + Alternatively add a save button somewhere...
      + Alternatively have a cron task that periodically writes to the db.
        + Though I did shoot this idea down earlier.
+ [ ] Highlight the active account.
+ [ ] Ledger summary bar providing:
      + # of transactions
      + Online Balance
      + Available Balance
      + Current Ledger Balance
+ [ ] Add smart name matching for payee
      + If there are 500 instances of "Kelly" and then 1 instance of "Kely",
        then perhaps that's just a typo...
      + That's what levenshtein_comparison.py is for.
+ [ ] Get category display working correctly
      + It should look like: "Expense:Entertainment:Bars" rather than just
        "Bars".
+ [ ] Replace all logging with lazy evaluation:
      + Right now, I use `logging.debug("{}".format(var))`, which will always
        evaluate the string
      + Switch to `logging.debug("%s", var)` and then the evaluation of the
        string will only happen if the debug message is to be displayed.
      + See http://stackoverflow.com/q/21377020/1354930
      + See http://stackoverflow.com/q/4148790/1354930
      + See http://stackoverflow.com/q/19462286/1354930
+ [ ] OFX Downloader
      + I did some work on this based on ofxclient
      + Don't actually save the OFX file if I can avoid it
        + Use a stream directly to the parser.
+ [ ] Decide on OFX Parser
      + ofxclient: last updated Mar 2013, really a cmd-line util, but does
        seem to include a parser
        + https://github.com/captin411/ofxclient
      + ofxparse: last updated Aug 2015. Is actually a parser and apparently
        supports Python3
        + https://github.com/jseutter/ofxparse
      + ofxtools: last updated Oct 2015. I vaguely recall thinking that this
        was my best bet, especially since it also has some SQLAlchemy support.
        I think one problem I has with it was that it relies on a config
        file for the downloading... hmm...
        + https://github.com/csingley/ofxtools
      + Roll my own. I did some fairly significant work on this, take a lot
        from Jerry Seutter's ofxparse (https://github.com/jseutter/ofxparse)
+ [ ] wx.PopupMenu for right-click menus
+ [ ] Google Wallet OFX?
+ [ ] Remove as much of the direct SQL as possible - I should be using
      SQLAlchemy for the entire backend.
+ [ ] Remove the ledger's database View?
      + SQLAlchemy doesn't like views very much
      + I should be able to do all the needed joins during the
        gui.LedgerGridBaseTable._get_value, but would that have too much
        overhead?
      + The view also makes it easy to look at the file using a different
        program...
+ [ ] Full OFX file parsing and import to database
+ [ ] Transaction matching to avoid entering duplicates
+ [ ] Match to Manualy Entered transaction
      + if match, then replace the manually entered transction TID with
        the downloaded one
+ [ ] Manually entered transctions TID should be null or negative so that
      it never conflicts with the FITID (Financial Institution Transaction ID)
      from the OFX.
+ [ ] Full suite of unit tests...
+ [ ] rename transaction tid to fitid
      + note that the fitid must be unique within scope of an account, but
        need not be sequential or even increasing. FITIDs are not unique
        across FIs (Financial Institutions). FI + ACCTID + FITID should be
        used as a global unique key.
+ [ ] rename institution ofx_id to fid, add org column?
      + or is that part of the ofx table?
+ [ ] If a direct-download of OFX is not avialble, have something that allows
      the user to automate it from the FI website.
+ [ ] Need Merchange Category Codes (MCCs)
      + https://en.wikipedia.org/wiki/Merchant_category_code
      + https://github.com/greggles/mcc-codes is a good source. Would also
        like to auto-update that...
      + See my fork of greggles's mcc-codes.
+ [ ] SQL Injection testing
+ [ ] General code cleanup and commenting
+ [ ] logging wrapper for functions
      + need to make sure the saved function name is correct
      + see douglib.utils and douglib.decorators I think...
      + See TPEdit's main.logged function.
+ [ ] Renaming Rules
+ [ ] Pareto plots of spending categories
+ [ ] If pybank file does not exist, creating it using the SQLAlchemy ORM
+ [ ] Organize the TODO list...
