def convert(input):
	if isinstance(input, dict):
		return {convert(key): convert(value) for key, value in input.iteritems()}
	elif isinstance(input, list):
		return [convert(element) for element in input]
	elif isinstance(input, unicode):
		return input.encode('utf-8')
	else:
		return input

def list_to_tuple_string(lst, to_remove=None):
	trans = string.maketrans('[]', '()')
	fields = str(lst).translate(trans, to_remove)
	return fields

def list_to_fields(lst):
	return list_to_tuple_string(lst, '\'')

def list_to_values(lst):
	return list_to_tuple_string(lst)