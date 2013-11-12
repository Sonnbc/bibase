import cql, string
import util, expression
from setting import settings
import re
from threading import Thread
import nltk

def make_connection():  
    return cql.connect(
        host = settings['host'], port = settings['port'], 
        keyspace = settings['keyspace'], cql_version = '3.0.0')

class Adapter:
    
    def __init__(self):
        self._connection = make_connection()

    def close(self) :
        self._connection.close()
    
    #TODO: fix 20000
    def count_lookup(self, field, value):
        if field not in settings['searchable_fields']:
            return 20000

        cursor = self.make_cursor()
        token = self.lookup_token(field, value)
        query = 'SELECT count(*) FROM lookup WHERE thing=:token limit 20000'
        
        cursor.execute(query, dict(token=token))
        res = cursor.fetchone()
        cursor.close()

        return res[0]    

    def getmany(self, keys, fields=settings['fields']):
        if not isinstance(keys, list):
            keys = [keys]
        if not isinstance(fields, list):
            fields = [fields]

        holder, arg = util.values_holder(keys)
        fs = util.fields_string(fields, False)

        cursor = self.make_cursor()
        query = ''.join(['SELECT ', fs, ' FROM main WHERE key IN ', holder])
        cursor.execute(query, arg)
        rows = cursor.fetchall() #TODO: dangerous? 
        cursor.close()
        return [self.row_to_entry(r, fields) for r in rows] if rows else []

    def get(self, key, extra, fields = settings['fields']):
        fs = util.fields_string(fields, False)
        cursor = self.make_cursor()
        query = ''.join(['SELECT ', fs, 
            ' FROM main WHERE key=:key AND extra=:extra'])
        arg = dict(key=key, extra=extra)
        cursor.execute(query, arg)
        row = cursor.fetchone()
        cursor.close()
        return self.row_to_entry(row, fields) if row else None

    def getmany_lookup(self, clauses, fields=settings['lookup_fields']):
        tokens = [self.lookup_token(*clause) for clause in clauses]
        cursor = self.make_cursor()
        holder, arg = util.values_holder(tokens)
        fs = util.fields_string(fields, False)

        query = ''.join(['SELECT ', fs, ' FROM lookup WHERE thing IN ', holder])
        cursor.execute(query, arg)
        
        rows = cursor.fetchall() #TODO: dangerous??
        cursor.close()
        return [self.row_to_entry(r, fields) for r in rows] if rows else []    

    def delete(self, key, extra):
        entry = self.get(key, extra)
        if not entry:
            return

        #remove from main
        cursor = self.make_cursor()
        cursor.execute('DELETE FROM main WHERE key=:key AND extra=:extra',
            dict(key=key, extra=extra))

        #remove from lookup
        tokens = self.lookup_tokens(entry)
        holder, arg = util.values_holder(tokens)
        query = ''.join(['DELETE FROM lookup WHERE thing IN ',
            holder, ' AND key=:key AND extra=:extra'])
        arg['key'] = key
        arg['extra'] = extra
        cursor.execute(query, arg)
        cursor.close

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
    
        fields = [field for field in entry.keys() 
            if field in settings['lookup_fields'] if entry[field]]

        holder, arg = util.values_holder([entry[field] for field in fields])

        #append thing to holder and field
        fields.append('thing')
        holder = holder[:-1] + ',:thing)'

        query = ''.join( ['INSERT INTO lookup ', util.fields_string(fields),
            ' VALUES ', holder] )
        
        cursor = self.make_cursor()
        for token in self.lookup_tokens(entry):
            arg['thing'] = token
            cursor.execute(query, arg)

        cursor.close()

    #TODO: check for title too, in case of update
    def insert(self, entry):
        entry = self.keyed_entry(entry)
        
        existings = self.getmany(entry['key'], ['extra', 'title'])
        old_entry = next((e for e in existings 
            if e['title'].lower()==entry['title'].lower()), None)
        print old_entry
        if old_entry:
            entry['extra'] = old_entry['extra']
            #need to remove entries from lookup first
            self.delete(entry['key'], entry['extra'])
        else:    
            extra = util.newest_extra([e['extra'] for e in existings])
            entry['extra'] = util.next_extra(extra)

        #print entry['extra']    
        self.unsafe_insert_main(entry)
        self.unsafe_insert_lookup(entry)

    #TODO: (note) if field is not searchable then count is zero
    #   so if cnf = (author=son or year=1992) then we don't query
    #   year=1992 at all. This means that unsearchable field can
    #   only be used at an AND filter, not an OR one.
    def search(self, search_query):
        print "start"
        cnf = expression.Expression(search_query).to_cnf()
        clauses = set([clause for disjunction in cnf for clause in disjunction])

        print "counting lookup"
        sizes = {clause:self.count_lookup(*clause) for clause in clauses}
        best = min(cnf, key=lambda x:sum(sizes.get(clause,0) for clause in x))

        print sizes
        print best
        entries = self.getmany_lookup([clause for clause in best
            if clause[0] in settings['searchable_fields'] ])
        print "done"
        return [entry for entry in entries if self.check_against_cnf(entry, cnf)]

    ###     
    #helper functions:  
    ###

    def make_cursor(self):
        return self._connection.cursor()

    def lookup_token(self, field, value):    
        return '%s=%s' % (field, value)

    def lookup_tokens(self, entry):
        tokens = []
        for field in settings['searchable_fields']:
            if entry.get(field, None):
                field_tokens = [self.lookup_token(field, value)
                    for value in util.nice_tokens(entry[field])]
                tokens = tokens + field_tokens
        return set(tokens)

    def row_to_entry(self, row, fields):
        return dict(zip(fields, row)) if row else None

    def keyed_entry(self, entry):
        res = dict(entry)
        if 'key' not in res:
            res['key'] = util.compute_key(res)
        return res

    def check_against_cnf(self, entry, cnf):
        return all(
                any(clause[1] in util.nice_split(entry[clause[0]])
                    for clause in disjunction)
                for disjunction in cnf)    

if __name__ == '__main__':

    item1 = {'author': 'Son Nguyen and Indy Gupta', 'year': 2012, 
        'title': 'stack over flow 2', 'journal': 'whatever'}
    item2 = {'author': 'Son Nguyen and Indy Gupta', 'year': 2012,
        'title': 'range check error 2 cool'}    
    
    adapter = Adapter()
    adapter.insert(item1)
    adapter.insert(item2)
    #adapter.delete('nguyeng2012', 1)
    #adapter.delete('nguyeng2012', 2)

    # s = """
    #     (author = han and author = wang and year=2008) or 
    #     ((year=2005 or title=system) and (author = gupta))"""

    # res = adapter.search(s)
    # print len(res)
    #for x in res:
    #    print util.nice_entry(x)




    


