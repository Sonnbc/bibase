#CREATE KEYSPACE dblp5 WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor': 3};

import json, cql

import controller
from setting import settings

_fields = """author varchar, editor varchar, title varchar, 
    booktitle varchar, pages varchar, year int, 
    address varchar, journal varchar, volume varchar, 
    number varchar, month varchar, url varchar, 
    ee varchar, cdrom varchar, cite varchar, 
    publisher varchar, note varchar, crossref varchar, 
    isbn varchar, series varchar, school varchar, 
    chapter varchar, papertype varchar,
    key varchar, extra int"""

_main = ''.join(["CREATE TABLE main (PRIMARY KEY (key, extra), ", 
    _fields, ')'])

_lookup = ''.join(["""CREATE TABLE lookup (thing varchar, 
    PRIMARY KEY (thing, key, extra), """,
    _fields, ')'])


def initialize():
    connection = controller.make_connection()
    cursor = connection.cursor()

    #create the main table
    cursor.execute(_main)

    #create lookup tables
    cursor.execute(_lookup)
    
    cursor.close()
    connection.close()


if __name__ == '__main__':
    initialize()


