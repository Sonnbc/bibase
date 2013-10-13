from controller import Controller
import sys
import json

_controller = Controller()

def add(item):
	_controller.insert(item)

def get(key):
	pass
def search(query):
	tokens = [x for x in query.split() if len(x) > 2]
	
	numbers = set([int(x) for x in tokens if x.isdigit()])

	author_result = _controller.lookup('author', tokens)

	total = [x for x in author_result if x['year'] in numbers] if numbers else author_result

	result = {}
	for item in total:
		result[item['key']] = {field: value for field, value in item.iteritems() if value}
	return result.values()


if __name__ == "__main__":
	if (sys.argv[1] == 'add'):
		print(sys.argv[2])
		with open(sys.argv[2]) as data:
			add(json.load(data))
	else:	
		res = search(sys.argv[1])
		for idx, item in enumerate(res):
			print idx, item 