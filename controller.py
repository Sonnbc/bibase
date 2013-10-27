import cql, string
import util, expression
from setting import settings
import re
from threading import Thread

def make_connection():	
	return cql.connect(
		host = settings['host'], port = settings['port'], 
		keyspace = settings['keyspace'], cql_version = '3.0.0')

class Controller:
	
	def __init__(self):
		self._connection = make_connection()

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

	def getmany(self, keys):
		cursor = self.make_cursor()
		holder, arg = util.values_holder(keys)

		query = ''.join(['SELECT * FROM main WHERE key IN ', holder])
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
		holder, arg = util.values_holder(tokens)

		query = ''.join(['DELETE FROM lookup WHERE thing in ',
			holder, ' AND key=:key'])
		arg['key'] = key

		cursor.execute(query, arg)
		cursor.close()

	def unsafe_insert_main(self, entry):
		fields = [field for field in entry.keys() 
			if field in settings['fields']]

		holder, arg = util.values_holder([entry[field] for field in fields])
		query = ''.join( ['INSERT INTO main ', util.fields_string(fields), 
			' VALUES ', holder] )

		cursor = self.make_cursor()
		cursor.execute(query, arg)
		cursor.close()

	def unsafe_insert_lookup(self, entry):
		#create a copy to keep the original intact
		entry = self.keyed_entry(entry)
		entry['thing'] = None

		fields = [field for field in entry.keys() 
			if field in settings['lookup_fields']]
		fields.append('thing')

		holder, arg = util.values_holder(entry[field] for field in fields)
		query = ''.join( ['INSERT INTO lookup ', util.fields_string(fields),
			' VALUES ', holder] )
		
		cursor = self.make_cursor()
		for token in self.lookup_tokens(entry):
			arg['thing'] = token
			cursor.execute(query, arg)

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

	def count_lookup(self, token, value):
		cursor = self.make_cursor()
		cursor.execute('SELECT count(*) FROM lookup WHERE thing=:value limit 20000', 
			dict(value=value))
		res = cursor.fetchone()
		cursor.close()
		return res[0]

	def getmany_lookup(self, values):
		cursor = self.make_cursor()

		holder, arg = util.values_holder(values)
		query = ''.join(['SELECT * FROM lookup WHERE thing in ', holder])
		print cursor.prepare_inline(query, arg)
		cursor.execute(query, arg)
		
		rows = cursor.fetchall() #TODO: dangerous??
		print len(rows)
		cursor.close()
		return [self.row_to_lookup_entry(row) for row in rows] if rows else []

	def check(self, entry, cnf):
		import nltk
		return all(
				any(clause[1] in nltk.word_tokenize(unicode(entry[clause[0]]).lower())
					for clause in disjunction)
				for disjunction in cnf)

	#TODO: (note) if field is not searchable then count is zero
	#	so if cnf = (author=son or year=1992) then we don't query
	#   year=1992 at all. This means that unsearchable field can
	#   only be used at an AND filter, not an OR one.
	def search(self, search_query):
		cnf = expression.Expression(search_query).to_cnf()
		clauses = set([clause for disjunction in cnf for clause in disjunction
			if clause[0] in settings['searchable_fields'] ])

		sizes = {clause:self.count_lookup(*clause) for clause in clauses}
		best = min(cnf, key=lambda x:sum(sizes.get(clause,0) for clause in x))

		print sizes
		print best
		entries = self.getmany_lookup([clause[1] for clause in best
			if clause[0] in settings['searchable_fields'] ])
		print "done"
		return [entry for entry in entries if self.check(entry, cnf)]

	###		
	#helper functions:	
	###

	def keyed_entry(self, entry):
		res = dict(entry)
		if 'key' not in res:
			res['key'] = util.compute_key(res)
		return res

if __name__ == '__main__':
	
	# item = {'author': 'Son Nguyen and Jiawei Han', 'year': 2012, 
	# 	'title': 'stack over flow'}
	
	# con = Controller()
	# con.insert(item)
	#a = con.disjuntion_solver([('author', 'danilevsky')])
	#print a

	con = Controller()
	s = """
		(author = han and author = wang) or 
		((year=2005 or title=system) and (author = gupta))"""
	
	res = con.search(s)
	print len(res)
	#for entry in res:
	#	print {field:entry[field] for field in entry if entry[field]}
