from controller import Controller
import sys
import json
import util

_controller = Controller()

def add(item):
	_controller.insert(item)

def delete(key):
	_controller.delete(item)

def get(key):
	pass

#TODO: refactor this
def is_good(query, entry):
	for field in query:
		if field not in entry:
			continue

		if isinstance(query[field], int):
			if query[field] != entry[field]:
				return False
		else:
			if any(token not in entry[field] for token in query[field].split()):
				return False
	return True
				
def search(query):
	tokens = _controller.lookup_tokens(query)

	for entry in _controller.search(tokens):
		if is_good(query, entry):
			print {field:entry[field] for field in entry if entry[field]}

if __name__ == "__main__":
	op = sys.argv[1]
	
	if (op == 'add'):
		with open(sys.argv[2]) as data:
			add(util.convert(json.load(data)))
	elif (op == 'search'):	
		with open(sys.argv[2]) as data:
			search(util.convert(json.load(data)))
	elif (op == 'delete'):
		delete(sys.argv[2])