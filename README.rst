======
PyBank
======
Personal accounting software. Alternative to the likes of Quicken, iBank,
Mint.com, and GnuCash.


Build Status
------------

+-----------+----------+-----------+------+
| Travis-CI | AppVeyor | Coveralls | PyPI |
+===========+==========+===========+======+
||travis-ci|||appveyor|||coveralls|||PyPI||
+-----------+----------+-----------+------+

+------------------------------------+
|            Downloads               |
+=========+=========+========+=======+
||DLTotal|||DLMonth|||DLWeek|||DLDay||
+---------+---------+--------+-------+

TODO: Downloads currently targeting wafer_map

Contents
--------

+ `Build Status`_
+ `Contents`_
+ `Summary`_
+ `Features`_
+ `Notes`_

Summary
-------
PyBank is personal account software similar to Quicken, iBank, and GnuCash.
It features the ability to download transactions via OFX, parse them, and
insert them into the local database.

Features
--------
+ Cross-Platform GUI via wxPython
+ Transaction download via OFX
+ Password Vault using the Host Environment's credential manager

  + Windows: Windows Credential Vault
  + Linux: Secret Service
  + Max: OSX Keychain

+ Lightweight storage of data via SQLite
+ TODO: Encrypt SQLite file
+ Categorize and label transactions
+ Payee renaming
+ Simple plotting features:

  + Pareto Plot of spending categories
  + Line Chart of Account value over time
  + Predicted balances based on previous spending, accounting for planned
    expenses

+ Handle multiple accounts in a single file

Notes
-----
None Yet

.. |travis-ci| image:: https://api.travis-ci.org/dougthor42/PyBank.svg?branch=master
  :target: https://travis-ci.org/dougthor42/PyBank
  :alt: Travis-CI (Linux, Max)

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/dougthor42/pybank?branch=master&svg=true
  :target: https://ci.appveyor.com/project/dougthor42/pybank
  :alt: AppVeyor (Windows)

.. |coveralls| image:: https://coveralls.io/repos/dougthor42/PyBank/badge.svg?branch=master
  :target: https://coveralls.io/r/dougthor42/PyBank?branch=master
  :alt: Coveralls (code coverage)

.. |PyPI| image:: http://img.shields.io/pypi/v/wafer_map.svg?style=flat
  :target: https://pypi.python.org/pypi/wafer_map/
  :alt: Latest PyPI version

.. |DLMonth| image:: http://img.shields.io/pypi/dm/wafer_map.svg?style=flat
  :target: https://pypi.python.org/pypi/wafer_map/
  :alt: Number of PyPI downloads per Month

.. |DLTotal| image:: http://img.shields.io/pypi/d/wafer_map.svg?style=flat
  :target: https://pypi.python.org/pypi/wafer_map/
  :alt: Number of PyPI downloads

.. |DLWeek| image:: http://img.shields.io/pypi/dw/wafer_map.svg?style=flat
  :target: https://pypi.python.org/pypi/wafer_map/
  :alt: Number of PyPI downloads per week

.. |DLDay| image:: http://img.shields.io/pypi/dd/wafer_map.svg?style=flat
  :target: https://pypi.python.org/pypi/wafer_map/
  :alt: Number of PyPI downloads per day