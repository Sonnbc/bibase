from controller import Controller
import sys

_controller = Controller()

def add(item):
	_controller.insert(item)

def get(key):
	pass
def search(query):
	tokens = [x for x in query.split() if len(x) > 2]
	
	numbers = [int(x) for x in tokens if x.isdigit()]
	year_result = _controller.lookup('year', numbers) if numbers else []

	author_result = _controller.lookup('author', tokens)

	total = author_result + year_result

	result = {}
	for item in total:
		result[item['key']] = {field: value for field, value in item.iteritems() if value}
	return result.values()


if __name__ == "__main__":
	if (sys.argv[1] == 'add'):
		add(sys.argv[2])
	else:	
		res = search(sys.argv[1])
		for idx, item in enumerate(res):
			print idx, item 