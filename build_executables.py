# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:08:24 2015

@author: dthor
"""

# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
import sys
import logging
import os.path
import glob

# Third Party
from cx_Freeze import setup, Executable

# Package / Application
from pybank import (__version__,
                    __project_url__,
                    __project_name__,
                    __description__,
                    __long_descr__,
                    )

# ---------------------------------------------------------------------------
### General Setup
# ---------------------------------------------------------------------------
# turn off logging if we're going to build a distribution
logging.disable(logging.CRITICAL)


# ---------------------------------------------------------------------------
### build_exe Setup
# ---------------------------------------------------------------------------
# included packages and their submodules
packages = [
#            'scipy.stats',
#            'scipy',
            'numpy',
            'keyring',
            'cryptography',
            'cffi',                 # needed by cryptography
            'win32timezone',        # needed by keyring?
            ]

# included modules
includes = [
            "pybank/pbsql",
            "pybank/plots",
            "pybank/crypto",
            "pybank/gui",
#            "scipy/special/ufuncs_cxx",
#            "scipy/special/ufuncs",
            ]

# Files to include (and their destinations)
include_files = [
                 "pybank\\test_database.db",
                 ("log\\README.txt", "log\\README.txt"),  # (source, dest)
#                 ("C:\\WinPython34_x64\\python-3.4.3.amd64\\Lib\\site-packages\\scipy\\special\\_ufuncs.pyd", "_ufuncs.pyd"),
#                 ("C:\\WinPython34_x64\\python-3.4.3.amd64\\Lib\\site-packages\\scipy\\special\\_ufuncs_cxx.pyd", "_ufuncs_cxx.pyd"),
                 ]

# list of names of files to include when determining dependencies of
# binary files that would normally be excluded; note that version
# numbers that normally follow the shared object extension are
# stripped prior to performing the comparison
bin_includes = [

                ]

# list of names of moduels to exclude
excludes = [
            "tkinter",
            "ssl",
            "pillow",
            "pil",
            "PyQt4",
            "multiprocessing",
            "bz2",
            "coverage",
            "zmq",
            ]

mplBackendsPath = os.path.join(os.path.split(sys.executable)[0],
                               "Lib\\site-packages\\matplotlib\\backends\\backend_*")

fileList = glob.glob(mplBackendsPath)

moduleList = []

for mod in fileList:
    module = os.path.splitext(os.path.basename(mod))[0]
    if not module in ("backend_wxagg", "backend_wx", "backend_agg"):
        moduleList.append("matplotlib.backends." + module)

#excludes += moduleList

# Options for build_exe
build_exe_opts = {
                  "packages": packages,
                  "includes": includes,
                  "include_files": include_files,
#                  "bin_includes": bin_includes,
                  "excludes": excludes,
                  "silent": True,
                  "include_msvcr": True,
                  }


# ---------------------------------------------------------------------------
### Executable Definitions
# ---------------------------------------------------------------------------
file_to_build = "pybank\\main.py"

# Application Base
base = None
#if sys.platform == 'win32':        # uncomment this to remove console window.
#    base = "Win32GUI"

exe1 = Executable(file_to_build,
                  base=base,
                  targetName="PyBank.exe",
                  )

# List of which executables to build.
exes_to_build = [
                 exe1,
                 ]


# ---------------------------------------------------------------------------
### setup()
# ---------------------------------------------------------------------------
setup(
    name=__project_name__,
    version=__version__,
    description=__description__,
    options={"build_exe": build_exe_opts},
    executables=exes_to_build,
)
