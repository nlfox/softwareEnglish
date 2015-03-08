# -*- coding: utf-8 -*-
__author__ = 'nlfox'
import sqlite3
conn = sqlite3.connect('/home/nlfox/data/result.db')
cursor = conn.execute("select * from resultdb_medium")
for row in cursor:
    print str(row)
