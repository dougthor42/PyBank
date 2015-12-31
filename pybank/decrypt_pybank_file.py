# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 16:39:58 2015

@author: dthor
"""

import crypto
import sqlite3
from contextlib import closing
import os

# Cryptography stuff
salt = crypto.get_salt()
pw = crypto.get_password()
peppered_pw = crypto.encode_and_pepper_pw(pw)
key = crypto.create_key(peppered_pw, salt)


# File to decrypt and to save as
file = "test_database.pybank"
new_file = "test_database_decrypt.db"

# Delete new_file if it esists
try:
    os.remove(new_file)
except PermissionError:
    raise
except FileNotFoundError:
    pass

dump = crypto.encrypted_read(file, key)

with closing(sqlite3.connect(new_file)) as conn:
    with closing(conn.cursor()) as cursor:
        for cmd in dump.decode('utf-8').split(';')[:-2]:

            # Replace any None values with NULL
            # TODO: Make this much more robust... For example, if I have
            #       name that's "None of your business". It will then become
            #       "NULL of your business".
            cmd = cmd.replace("None", "NULL")
            print(cmd)
            cursor.execute(cmd)
            conn.commit()
