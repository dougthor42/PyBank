# -*- coding: utf-8 -*-
"""
Tests OFX components.

Created on Tue May 12 13:31:46 2015

Usage:
    test_ofx.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""

# Standard Library
import sys
import unittest
import unittest.mock as mock
import os.path as osp

# Third-Party
from docopt import docopt

# Package / Application
try:
    from .. import ofx
except (SystemError, ImportError):
    if __name__ == "__main__":
        # Allow module to be run as script
        print("Running module as script")
        sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
        import ofx
    else:
        raise




def main():
    """
    Main entry point
    """
    docopt(__doc__, version="0.0.1")    # TODO: pull VERSION from __init__
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
