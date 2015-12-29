# -*- coding: utf-8 -*-
"""
Updates the 'category' table from the categories.txt file

Created on Mon Dec  7 22:39:05 2015

@author: dthor
"""

import sqlite3

#with open("../../doc/categories.txt") as openf:
#    print(openf.read())
#
#conn = sqlite3.connect("../../blank_db_test.sqlite")
#cursor = conn.cursor()
#
#with open("../../doc/categories.txt") as openf:
#    for line in openf:
        # 1. check if the line is splittable.
        # 2. if so, split out only the very last element.
        # 3. check if th

def recurse(items, delim='.', retval=None):
    """
    recuse through all of the elements, finding parents.

    if parent = 1, stop

    then,
    """
    if retval is None:
        retval = []

    # try and split the item
    split_item = item.split(delim)
    if len(split_item) == 1:
        print("adding {}.".format(item))
    else:
        recurse(delim.join(split_item[:-1]), delim)


def thing(items, delim):
    index = 1           # sqlite is 1-indexed!
    categories = {}
    for item in items:
        # does the item have a parent?
        item = item.strip()
        split = item.split(delim)
        if len(split) == 1:
            # no, it does not have a parent
            categories[item] = (index, index)
        else:
            # yes, it does have a parent
            # look up that parent in the categories list
            parent_item = delim.join(split[:-1])
            parent = categories[parent_item][0]
            categories[item] = (index, parent)
        index += 1
    return categories


def sort_categories(categories):
    """ converts the categories to a list for adding to a database """
    return sorted([(i, k, parent) for (k, (i, parent)) in categories.items()])


def write_to_db(items, delim):
    conn = sqlite3.connect("../../pybank/test_database.db")
    cursor = conn.cursor()

    for item in items:
        item = list(item)
        item[1] = item[1].split(delim)[-1]
        item = tuple(item)
        sql = "INSERT INTO category VALUES{};".format(item)
        print(sql)
        cursor.execute(sql)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    with open("../../doc/categories.txt") as openf:
        data = [line for line in openf]

    a = thing(data, ":")
    b = sorted([(i, k, parent) for (k, (i, parent)) in a.items()])

#    for item in b:
#        print(item)

    write_to_db(b, ":")

    """
    So what I currently have won't work, and here's why:
        If an end item of the same name is found, it's overwritten.

    What if I use the index for the dict key instead of the name....
    """


    data1 = "Expense.Business.Travel.Hotel"
    data2 = "Expense.Travel.Hotel"
    adj_list = [(1, "Expense", 1),
                (2, "Business", 1),
                (3, "Travel", 2),
                (4, "Gas", 2),
                (5, "Hotel", 2),
                (6, "Airfair", 2),
                (7, "Travel", 1),
                (8, "Gas", 7),
                (9, "Hotel", 7),
                (10, "Airfair", 7),
                ]
    correct1 = (1, 2, 3, 5)
    correct2 = (1, 7, 9)
