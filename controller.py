from adapter import Adapter
from setting import settings
import util

import sys, json, re

def bib_string(entry):
    if entry['extra']:
        extra = '-%s' % entry['extra']
    else:
        extra = ''  
    fline = '@%s{%s%s,' % (entry['papertype'], entry['key'], extra)
    content = ',\n'.join(['    %s = {%s}' % (field, entry[field]) 
        for field in entry 
        if entry[field] and field in settings['bib_fields'] ])
    lline = '}'

    return '\n'.join([fline, content, lline])

class Controller:

    def __init__(self):
        self.adapter = Adapter()

    def insert(self, entry):
        self.adapter.insert(entry)

    def get(self, key):
        m = re.search('(\w+)-(\d+)', key)
        if m:
            key = m.groups()[0]
            extra = int(m.groups()[1])
            entry = self.adapter.get(key, extra)
            return [entry] if entry else None

        entries = self.adapter.getmany(key)
        if not entries:
            return None
        if len(entries) is 1:
            entries[0]['extra'] = None
            return [entries[0]]
        return entries
    
if __name__ == '__main__':
    con = Controller()
    keys = ['wanght2008', 'guptat2007', 
        'lencckn2010', 'guptat2007-1', 'guptat2007-11']

    for key in keys:
        entries = con.get(key)

        if not entries:
            print 'WARNING: no entries for %s--------------------' % key
            continue
        elif len(entries) > 1:
            print 'WARNING: multiple entries for %s--------------' % key
        else:
            print '-------------------------------------------------------'

        for x in entries:        
            print util.convert(bib_string(x))


                

            
