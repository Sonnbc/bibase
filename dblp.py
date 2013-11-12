from xml.etree.cElementTree import iterparse
from adapter import Adapter
from multiprocessing import Pool
import sys
from setting import settings
import threading
import cql

num_threads = 20
start_work_number = 50000
batch_count = start_work_number / num_threads



def add(tup):
    entries, begin, end = tup
    adapter = Adapter()

    not_implemented_error_count = 0
    error = 0

    #print (begin,end)
    for entry in entries[begin : end]:
        try:
            adapter.insert(entry)
        except cql.apivalues.OperationalError:
           print sys.exc_info()
           print entry
           error += 1

    if not_implemented_error_count + error > 0:
        print begin, end, not_implemented_error_count, error

    adapter.close()

source = "dblp/utf8.xml"

types = ['article','inproceedings','book','incollection', 'proceedings',
                'phdthesis','mastersthesis','www']

context = iterparse(source, events=("start", "end"))
context = iter(context)

event, root = context.next()
count = 0
entries = []

pool = Pool(num_threads)
weirds = ['i', 'sub', 'sup', 'tt']

for event, elem in context:
    if event == "start" and elem.tag in types:
        item = {'papertype': elem.tag}
    elif event == "end" and elem.tag in types:
        #TODO: fix these cases: 
        # <title><weird>stu <weird>Black Holes Unveiled.</title>

        
        if ('author' not in item or 'year' not in item 
            or any(weird in item for weird in weirds) ):
            continue

        #lst = [key for key in item if key not in settings['fields']]
        #if lst:
        #   print lst

        item['author'] = ' and '.join(item['author'])
        item['year'] = int(item['year'])
        if item['title'][-1] == '.':
            item['title'] = item['title'][:-1]

        count = count + 1
        entries.append(item)
        if len(entries) == start_work_number:
            print "---------------------------start work", count
            # threads = []
            # for i in xrange(0, num_threads):
            #   t = threading.Thread(target=add, 
            #       args=(entries, i*batch_count, (i+1)*batch_count) )
            #   threads.append(t)

            # for t in threads:
            #   t.start()
            # for t in threads:
            #   t.join()    

            args_list = [(entries, i*batch_count, (i+1)*batch_count) 
                for i in xrange(0, num_threads)]
            
            pool.map(add, args_list)
            #add( (entries, 0, len(entries)) )  
            del entries[:]
        
        
        
        root.clear()
        item = {}
    elif event == 'end' and elem.tag == 'author':
        item.setdefault('author', []).append(elem.text)
    elif event == "end" and elem.tag != 'dblp':
        item[elem.tag] = elem.text

if entries:
    add( (entries, 0, len(entries)) )






