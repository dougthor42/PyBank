# -*- coding: utf-8 -*-
"""
Created on Tue May 12 12:58:55 2015

@author: dthor
"""
### #------------------------------------------------------------------------
### Imports
### #------------------------------------------------------------------------
# Standard Library
import os
import sys
from setuptools import setup, find_packages

# Third Party

# Package / Application


# Read the "__about__" file.
# This is how the `cryptography` package does it. Seems like a decent
# way because it prevents the main package from being imported.
# I'm not sure how I feel about `exec()` though...
about = {}
base_dir = os.path.dirname(__file__)
sys.path.insert(0, base_dir)
with open(os.path.join(base_dir, "pybank", "__about__.py")) as f:
    exec(f.read(), about)

with open(os.path.join(base_dir, "README.rst")) as f:
    long_description = f.read()

# See https://chriswarrick.com/blog/2014/09/15/python-apps-the-right-way-entry_points-and-scripts/
# See http://stackoverflow.com/a/9615473/1354930
entry_points = {
    'gui_scripts': ['pybank = pybank.__main__:main'],
}

classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    "Environment :: Win32 (MS Windows)",
    "Environment :: X11 Applications",
    "Environment :: MacOS X",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Financial and Insurance Industry",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Office/Business :: Financial",
    "Topic :: Office/Business :: Financial :: Accounting",
    "Topic :: Utilities",
]

setup(
    name=about["__package_name__"],
    version=about["__version__"],

    description=about["__description__"],
    long_description=long_description,
    url=about["__project_url__"],

    author=about["__author__"],
    license=about["__license__"],

    entry_points=entry_points,
    packages=find_packages(),
    classifiers=classifiers,

    requires=["wxPython",
              "keyring",
              "docopt",
              "BeautifulSoup4",
              ],
)