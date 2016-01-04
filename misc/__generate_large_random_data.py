# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 12:01:52 2015

@author: dthor
"""


from random import random, randint, choice
import sqlite3
import string

letters = string.ascii_letters

sql = """INSERT INTO transaction_0
(check_num, amount, payee_id, category_id, label_id, memo, fitid)
VALUES
(?, ?, ?, ?, ?, ?, ?)"""

def random_data(n):
    num = 0
    while num < n:
        yield (str(num),
               "{:0.2f}".format(random()*1000),
               str(randint(1, 100)),
               str(randint(200, 250)),
               str(randint(500, 550)),
               "".join(choice(letters) for _ in range(randint(1, 15))),
               str(randint(1000, 9999)),
               )
        num += 1

for item in random_data(10):
    print(item)

# fill a transaction table with random data
db_file = "C:\\WinPython34_x64\\projects\\github\\PyBank\\pybank\\test_database_large.db"
conn = sqlite3.connect(db_file)
cur = conn.cursor()
cur.executemany(sql, random_data(4000))
conn.commit()
cur.close()
conn.close()
