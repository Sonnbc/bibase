import cql, string
import util
from setting import settings
import re

def make_connection():	
	return cql.connect(
		host = settings['host'], port = settings['port'], 
		keyspace = settings['keyspace'], cql_version = '3.0.0')

class Controller:
	
	def __init__(self):
		self._connection = make_connection()

	def close(self)	:
		self._connection.close()
	
	def lookup_tokens(self, entry):
		tokens = []
		for field in settings['lookup_fields']:
			if entry.get(field, None):
				tokens = tokens + util.nice_tokens( entry[field] ) 
		return set(tokens)

	def row_to_entry(self, row):
		return dict(zip(settings['fields'], row)) if row else None

	def get(self, key):
		cursor = self._connection.cursor()
		cursor.execute('SELECT * FROM main WHERE key=:key', dict(key=key))
		row = cursor.fetchone()
		cursor.close()
		return self.row_to_entry(row)

	def getmany(self, keys):
		cursor = self._connection.cursor()
		query = ''.join(['SELECT * FROM main WHERE key IN ', 
			util.values_holder(keys)])
		arg = {key:key for key in keys}
		cursor.execute(query, arg)
		rows = cursor.fetchall() #TODO: dangerous? 
		cursor.close()
		return [self.row_to_entry(row) for row in rows] if rows else None

	def delete(self, key):
		entry = self.get(key)
		if not entry:
			return 
		
		#remove from main
		cursor = self._connection.cursor()			
		cursor.execute('DELETE FROM main WHERE key=:key', dict(key=key))

		#remove from lookup
		tokens = self.lookup_tokens(entry)
		query = ''.join(['DELETE FROM lookup WHERE thing in ',
			util.values_holder(tokens), ' AND key=:key'])
		arg = {token:token for token in tokens}
		arg['key'] = key

		cursor.execute(query, arg)

		cursor.close()

	def unsafe_insert_main(self, entry):
		fields = [key for key in entry.keys() if key in settings['fields']]
		values = [entry[field] for field in fields]

		query = ''.join( ['INSERT INTO main ', util.fields_string(fields), 
			' VALUES ', util.values_holder(fields)] )

		cursor = self._connection.cursor()
		cursor.execute(query, entry)
		cursor.close()

	def unsafe_insert_lookup(self, entry):
		key = entry['key'] if 'key' in entry else util.compute_key(entry)

		tokens = self.lookup_tokens(entry)

		queries = (['INSERT INTO lookup (thing,key) VALUES (:token,:key)'] * 
			len(tokens) )
		args = [ [dict(token=token, key=key)] for token in tokens ]

		cursor = self._connection.cursor()
		cursor.executemany(queries, args)
		cursor.close()

	def insert(self, entry):
		#create a copy to keep the original intact
		entry = dict(entry)
		entry['key'] = util.compute_key(entry)
		
		old_entry = self.get(entry['key'])
		if old_entry:
			if util.is_close(old_entry['title'], entry['title']):
				raise NotImplementedError(
					'Different papers with the same key is unsupported.')
		
		self.unsafe_insert_main(entry)
		self.unsafe_insert_lookup(entry)

	def hack(self, s):
		return re.match('^[\w]+$', s) is not None

	#TODO: refractor this
	def search(self, tokens):
		tokens = [token.lower() for token in tokens]
		
		query = 'SELECT key FROM lookup WHERE thing=:token'
		
		cursors = [self._connection.cursor() for token in tokens]
		for i in xrange(len(tokens)):
			cursors[i].execute(query, dict(token=tokens[i]))

		print [cursor.rowcount for cursor in cursors]

		cursor = min(cursors, key=lambda x: x.rowcount)

		for other in cursors:
			if other is not cursor:
				other.close()

		cursor.arraysize = 10000
		buff = []
		while True:
			while not buff:
				#TODO: fix this
				keys = set( [x[0] for x in cursor.fetchmany() if self.hack(x[0])] )
				if not keys:
					break
				buff = self.getmany(keys) 
			#TODO: fix this
			if not buff:
				return	
			yield buff.pop()
		
		cursor.close()

if __name__ == '__main__':
	controller = Controller()
	# entry = {
	# 	'authors': 'R. L. Adam and Jawei Han and Son Nguyen',
	# 	'title': 'Firefox',
	# 	'year': 2007,
	# 	'isbn': '1234-567-8912'
	# }
	# controller.unsafe_insert_main(entry)

	#controller.delete('nguyenn1234')
	print controller.search(['asdasdasad'])