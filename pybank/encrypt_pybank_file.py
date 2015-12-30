# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 16:39:58 2015

@author: dthor
"""

import crypto
import sqlite3
from contextlib import closing
import os


def main():
    # Cryptography stuff
    salt = crypto.get_salt()
    pw = crypto.get_password()
    peppered_pw = crypto.encode_and_pepper_pw(pw)
    key = crypto.create_key(peppered_pw, salt)


    # File to encrypt and to save as
    file = "test_database.db"
    new_file = "test_database.pybank"

    # Delete new_file if it esists
    try:
        os.remove(new_file)
    except PermissionError:
        raise
    except FileNotFoundError:
        pass

    with closing(sqlite3.connect(file)) as conn:
        dump = list(conn.iterdump())
        dump = "".join(line for line in dump)
        dump = dump.encode('utf-8')

    crypto.encrypted_write(new_file, key, dump)


if __name__ == "__main__":
    main()