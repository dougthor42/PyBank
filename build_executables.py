# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:08:24 2015

@author: dthor
"""

import sys
from cx_Freeze import setup, Executable

build_exe_opts = {"includes": ["pybank/pbsql", ],
                  "include_files": ["pybank/test_database.db"],
                  "silent": True,
                  }

base = None
if sys.platform == 'win32':
    base = "Win32GUI"

exes_to_build = [Executable("pybank\gui.py", base=base),
                 ]

setup(
    name = 'PyBank',
    version = '0.0.1',
    description = "Finance tracking software",
    options = {"build_exe": build_exe_opts},
    executables = exes_to_build,
)