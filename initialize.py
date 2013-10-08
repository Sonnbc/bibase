import json
import cql
import controller

#TODO: change authors to author ??
_main = """CREATE TABLE main (key varchar PRIMARY KEY, 
	authors varchar, editor varchar, title varchar, 
	booktitle varchar, pages varchar, year int, 
	address varchar, journal varchar, volume varchar, 
	number varchar, month varchar, url varchar, 
	ee varchar, cdrom varchar, cite varchar, 
	publisher varchar, note varchar, crossref varchar, 
	isbn varchar, series varchar, school varchar, 
	chapter varchar, papertype varchar)"""

_author = """CREATE TABLE authorLookup (author varchar, 
	key varchar, PRIMARY KEY (author, key) )"""

_title = """CREATE TABLE titleLookup (title varchar, 
	key varchar, PRIMARY KEY (title, key) )"""

_year = """CREATE TABLE yearLookup (year int,
	key varchar, PRIMARY KEY (year, key) )"""

def initialize():
	queries = [_main, _author, _title, _year]
	args = [[]]*len(queries)

	connection = controller.make_connection()

	cursor = connection.cursor()
	cursor.executemany(queries, args)
	
	cursor.close()
	connection.close()


if __name__ == '__main__':
	initialize()


