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
		self.lookup_cache = {}

	def close(self)	:
		self._connection.close()
	
	def make_cursor(self):
		return self._connection.cursor()

	def lookup_tokens(self, entry):
		tokens = []
		for field in settings['searchable_fields']:
			if entry.get(field, None):
				tokens = tokens + util.nice_tokens( entry[field] ) 
		return set(tokens)

	def row_to_entry(self, row):
		return dict(zip(settings['fields'], row)) if row else None

	def row_to_lookup_entry(self, row):
		return dict(zip(settings['lookup_fields'], row)) if row else None

	def get(self, key):
		cursor = self.make_cursor()
		cursor.execute('SELECT * FROM main WHERE key=:key', dict(key=key))
		row = cursor.fetchone()
		cursor.close()
		return self.row_to_entry(row)

	#TODO: define this function more clearly. count() or not?
	def get_lookup(self, token, value):
		cursor = self.make_cursor()
		cursor.execute('SELECT * FROM lookup WHERE thing=:value', 
			dict(value=value))
		print cursor.result
		rows = cursor.fetchall()
		cursor.close()
		#return [self.row_to_lookup_entry(r) for r in rows] if rows else []
		return []

	def getmany(self, keys):
		cursor = self.make_cursor()
		query = ''.join(['SELECT * FROM main WHERE key IN ', 
			util.values_holder(keys)])
		arg = {key:key for key in keys}
		cursor.execute(query, arg)
		rows = cursor.fetchall() #TODO: dangerous? 
		cursor.close()
		return [self.row_to_entry(row) for row in rows] if rows else []

	def delete(self, key):
		entry = self.get(key)
		if not entry:
			return 
		
		#remove from main
		cursor = self.make_cursor()			
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
		fields = [field for field in entry.keys() if field in settings['fields']]

		query = ''.join( ['INSERT INTO main ', util.fields_string(fields), 
			' VALUES ', util.values_holder(fields)] )

		cursor = self.make_cursor()
		cursor.execute(query, entry)
		cursor.close()

	def unsafe_insert_lookup(self, entry):
		#create a copy to keep the original intact
		entry = self.keyed_entry(entry)
		entry['thing'] = None

		fields = [field for field in entry.keys() 
			if field in settings['lookup_fields']]

		query = ''.join( ['INSERT INTO lookup ', util.fields_string(fields),
			' VALUES ', util.values_holder(fields)] )
		
		cursor = self.make_cursor()
		for token in self.lookup_tokens(entry):
			entry['thing'] = token
			cursor.execute(query, entry)

		cursor.close()

	def insert(self, entry):
		entry = self.keyed_entry(entry)
		
		old_entry = self.get(entry['key'])
		if old_entry:
			if util.is_the_same(old_entry['title'], entry['title']):
				raise NotImplementedError(
					'Different papers with the same key is unsupported.')
		
		self.unsafe_insert_main(entry)
		self.unsafe_insert_lookup(entry)

	def lookup(self, clause):
		if clause not in self.lookup_cache:
			self.lookup_cache[clause] = self.get_lookup(*clause)
		
		return self.lookup_cache[clause]

	def disjuntion_solver(self, clauses):
		res = []
		for clause in clauses:
			res += self.lookup(clause)
		#there might be duplicate entries	
		return res	

	def hack(self, s):
		return re.match('^[\w]+$', s) is not None

	#TODO: refractor this
	def search(self, tokens):
		tokens = [token.lower() for token in tokens]
		
		query = 'SELECT key FROM lookup WHERE thing=:token'
		
		cursors = [self.make_cursor() for token in tokens]
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

	###		
	#helper functions:	
	###

	def keyed_entry(self, entry):
		res = dict(entry)
		if 'key' not in res:
			res['key'] = util.compute_key(res)
		return res

if __name__ == '__main__':
	
	item = {'author': 'Son Nguyen and Jiawei Han', 'year': 2012, 
		'title': 'stack over flow'}
	
	con = Controller()
	con.insert(item)
	#a = con.disjuntion_solver([('author', 'danilevsky')])
	#print a
