import json
import cql
import string
import util

#assume different keys for different paper
#this means Adam and Bob only write one paper in year 2007 whose key is AB2007

#initialize
with open('settings.json') as settingFile:
	_settings = util.convert(json.load(settingFile))

def make_connection():	
	return cql.connect(
		host = _settings['host'], port = _settings['port'], 
		keyspace = _settings['keyspace'], cql_version = '3.0.0')

class Controller:
	def __init__(self):
		self._connection = make_connection()

	def close(self)	:
		self._connection.close()

	def compute_key(self, item):
		tokens = [author.split()[-1][0] for author in item['authors'].split(' and ')]
		tokens.append(str(item['year']))
		key = ''.join(tokens).lower()
		return key

	def get(self, key):
		cursor = self._connection.cursor()
		cursor.execute('SELECT * FROM main WHERE key=:key', dict(key=key))
		row = cursor.fetchone()
		cursor.close()
		return dict(zip(_settings['fields'], row)) if row else None

	def get_many(self, keys):
		keys = [x.encode('utf8') for x in keys]
		l = '(\'' + '\',\''.join(keys) + '\')'
		cursor = self._connection.cursor()
		cursor.execute('SELECT * FROM main WHERE key in ' + l)
		rows = cursor.fetchall() #TODO: don't do this
		cursor.close()
		res = [dict(zip(_settings['fields'], row)) for row in rows]
		return [dict(zip(_settings['fields'], row)) for row in rows]

	def test(self, item):
		query = 'INSERT INTO main (key, authors, year, title) VALUES (:key, :authors, :year, :title)'
		cursor = self._connection.cursor()
		print cursor.prepare_inline(query, item)
		cursor.execute(query, item)
		cursor.close()

	def unsafe_insert(self, item):
		#trans = string.maketrans('[]', '()')
		#fields = str(item.keys()).translate(trans, '\'')
		#values = str(item.values()).translate(trans).replace(', u\'', ', \'') #TODO:make less hacky
		fields = util.list_to_fields(item.keys())
		values = util.list_to_values(item.values())
		
		query = ''.join(['INSERT INTO main ', fields, ' VALUES ', values])
		cursor = self._connection.cursor()
		cursor.execute(query)
		cursor.close()


	def unsafe_insert_lookup(self, field, values, key):
		cursor = self._connection.cursor()
		query = ''.join(['INSERT INTO ', field, 'lookup (', 
			field, ', key) VALUES (:value, :key)'])

		args = [[dict(value=value, key=key)] for value in values]
		
		cursor.executemany([query]*len(values), args)
		cursor.close()

	def lookup(self, field, values)	:
		l = str(values).replace('[','(').replace(']', ')')
		query = ''.join(['SELECT * FROM ', field, 'lookup WHERE ', 
			field, ' in ', l ])

		cursor = self._connection.cursor()
		cursor.execute(query)
		
		keys = [row[1] for row in cursor]
		dic = {}
		for key in keys:
			dic[key] = dic.get(key, 0) + 1

		max_count = dic[max(dic, key=dic.get)]
		best_keys = [key for key in dic if dic[key] == max_count]

		return self.get_many(best_keys) if best_keys else []

	def is_conflict(self, new, old):
		return any(field in new and new[field] != old[field] 
			for field in old if old[field])

	def insert(self, item):
		item['key'] = self.compute_key(item)

		#TODO: fix encoding
		old_item = self.get(item["key"])
		if old_item:
			if old_item['title'].lower() != item['title'].lower():
				raise NotImplementedError(
					'Different papers with the same key is unsupported.')
				return
			if self.is_conflict(item, old_item):
				#print old_item['journal']
				#print item['journal']
				raise ValueError('Conflicted detected. Cannot merge.')
				return
			print("Item exists. Merging...")

		self.unsafe_insert(item)

		#TODO: search for title
		authors = [author.split()[-1] for author in item['authors'].split(' and ')]
		self.unsafe_insert_lookup('author', authors, item['key'])

		self.unsafe_insert_lookup('year', [item['year']], item['key'])
	
if __name__ == '__main__':
	item = {
		'authors': 'R. L. Adam and Jawei Han and Son Nguyen',
		'title': 'Firefox',
		'year': 2007,
		'isbn': '1234-567-8912'
	}

	item2 = {
		'authors': 'R. L. Adam',
		'title': 'Chrome',
		'year': 2000
	}

	item3 = {
		'authors': 'author', 'editor': 'editor', 'title': 'title', 
		'booktitle': 'booktitle', 'pages': 'pages', 'year': 2000, 
		'address': 'address', 'journal': 'journal', 'volume': 'volume', 
		'number': 'number', 'month': 'month', 'url': 'url', 
		'ee': 'ee', 'cdrom': 'cdrom', 'cite': 'cite', 
		'publisher': 'publisher', 'note': 'note', 'crossref': 'crossref', 
		'isbn': 'isbn', 'series': 'series', 'school': 'school', 
		'chapter': 'chapter', 'papertype': 'papertype'
	}

	item4 = {
		'authors': 'R. L. Adam and Jawei Han and Son Nguyen',
		'title': 'Firefox',
		'year': 2007,
		'number': '123124'
	}
	
	controller = Controller()
	#controller.insert(item)
	#controller.insert(item2)
	#controller.insert(item3)
	#controller.insert(item)
	#controller.insert(item4)
	#controller.insert(item2)
	print(controller.lookup('author', ['Adam']))
	controller.close()
	
