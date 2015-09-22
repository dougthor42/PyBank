# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 12:32:58 2015

@author: dthor
"""

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import select

# Create the database engine.
# The databsse is not actually connected to at this point - it only connects
# when asked to perform a task on the DB.
engine = create_engine("sqlite:///:memory:", echo=True)

# A catalog. Not sure what this is...
metadata = MetaData()

# Create each table
users = Table("users", metadata,
              Column("id", Integer, primary_key=True),
              Column('name', String),
              Column('fullname', String),
              )

addresses = Table('addresses', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('user_id', None, ForeignKey('users.id')),
                  Column('email_address', String, nullable=False),
                  )

# tell the Metadata to create our tables inside the database
metadata.create_all(engine)

# Create an insert statement. Note that it's not executed
ins = users.insert().values(name='jack', fullname='Jack Jones')

# Can print the SQL:
print(ins)  # 'INSERT INTO users (name, fullname) VALUES (:name, :fullname)'
print(ins.compile().params)     # {'fullname': 'Jack Jones', 'name': 'jack'}

# Now actually connect to the database
conn = engine.connect()
print(conn)     # <sqlalchemy.engine.base.Connection object at 0x00000000077BC588>

# and execute our insert statement
result = conn.execute(ins)
print(result)

# note that we use questionmarks - that's due to the SQLite dialect.
# It we tell ins what dialect to expect, we can see the true SQL:
ins.bind = engine
print(ins)

# The normal way to create an insert statement:
ins = users.insert()
conn.execute(ins, id=2, name='wendy', fullname='Wendy Williams')

# Can do multiple inserts with a dict:
conn.execute(addresses.insert(),
             [{'user_id': 1, 'email_address' : 'jack@yahoo.com'},
              {'user_id': 1, 'email_address' : 'jack@msn.com'},
              {'user_id': 2, 'email_address' : 'www@www.org'},
              {'user_id': 2, 'email_address' : 'wendy@aol.com'},
              ]
             )

# Selecting:
s = select([users])
result = conn.execute(s)
for row in result:
    print(row)

# Can also select via dict and indexes:
result = conn.execute(s)
row = result.fetchone()
print("name: {}; fullname: {}".format(row['name'], row['fullname']))
print("name: {}; fullname: {}".format(row[1], row[2]))

# But apparently the best way is to use the Column objects directly as keys:
#   I think the 'c' stands for column
for row in conn.execute(s):
    print("name: {}; fullname: {}".format(row[users.c.name],
                                          row[users.c.fullname]))

# When done with the result, it's best to close it:
result.close()


# We can get more control over which columns are in the select:
s = select([users.c.name, users.c.fullname])
result = conn.execute(s)
for row in result:
    print(row)

# Adding a WHERE clause:
s = select([users, addresses]).where(users.c.id == addresses.c.user_id)
for row in conn.execute(s):
    print(row)

# Fancy: the `users.c.id == addresses.c.user_id` makes an object:
print(repr(users.c.id == addresses.c.user_id))
print(users.c.id == addresses.c.user_id)

