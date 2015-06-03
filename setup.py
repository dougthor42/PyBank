# -*- coding: utf-8 -*-
"""
Created on Tue May 12 12:58:55 2015

@author: dthor
"""

from setuptools import setup

setup(
    name = 'PyBank',
    version = '0.0.1',
    description = "Finance tracking software",
    packages=['pybank', 'pybank.tests'],
    author="Douglas Thor",
    url="https://github.com/dougthor42/PyBank",
    classifiers=[
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
        ],
    requires=["wxPython",
              "keyring",
              "docopt",
              "BeautifulSoup4",
              ],
)