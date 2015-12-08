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

def something(item, delim='.', retval=None):
    """ """
    # try and split the item
    split_item = item.split(delim)
    if len(split_item) == 1:
        print("adding {}.".format(item))
    else:
        something(delim.join(split_item[:-1]), delim)


def thing(items, delim):
    index = 1           # sqlite is 1-indexed!
    categories = {}
    for item in items:
        # does the item have a parent?
        item = item.strip()
        print(item)
        split = item.split(delim)
        if len(split) == 1:
            # no, it does not have a parent
            categories[item] = (index, index)
        else:
            # yes, it does have a parent
            # look up that parent in the categories list
            parent = categories[split[-2]][0]
            categories[split[-1]] = (index, parent)
        index += 1
    return categories


def sort_categories(categories):
    """ converts the categories to a list for adding to a database """
    return sorted([(i, k, parent) for (k, (i, parent)) in categories.items()])


def write_to_db(items):
    conn = sqlite3.connect("../../blank_db_test.sqlite")
    cursor = conn.cursor()

    for item in items:
        sql = "INSERT INTO category VALUES{};".format(item)
        cursor.execute(sql)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    with open("../../doc/categories.txt") as openf:
        data = [line for line in openf]

    a = thing(data, ":")
    b = sorted([(i, k, parent) for (k, (i, parent)) in a.items()])

    for item in b:
        print(item)

#    write_to_db(b)
