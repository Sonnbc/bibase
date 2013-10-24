import json, cql

import controller
from setting import settings, lookup_table_name


_main = """CREATE TABLE main (key varchar PRIMARY KEY, 
	author varchar, editor varchar, title varchar, 
	booktitle varchar, pages varchar, year int, 
	address varchar, journal varchar, volume varchar, 
	number varchar, month varchar, url varchar, 
	ee varchar, cdrom varchar, cite varchar, 
	publisher varchar, note varchar, crossref varchar, 
	isbn varchar, series varchar, school varchar, 
	chapter varchar, papertype varchar)"""

#_lookup = """CREATE TABLE :name (:field varchar, 
#	key varchar, PRIMARY KEY (:field, key) )"""

_lookup = """CREATE TABLE lookup (thing varchar, 
	key varchar, PRIMARY KEY (thing, key) )"""


def initialize():
	connection = controller.make_connection()
	cursor = connection.cursor()

	#create the main table
	cursor.execute(_main)

	# queries = [ _lookup.replace(':field', field).
	# 	replace(':name', lookup_table_name(field))
	# 	for field in settings['lookup_fields'] ]

	# args = [[]] * len(settings['lookup_fields'])

	# #create lookup tables
	# cursor.executemany(queries, args)

	cursor.execute(_lookup)
	
	cursor.close()
	connection.close()


if __name__ == '__main__':
	initialize()


