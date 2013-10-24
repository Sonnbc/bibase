import string
import nltk
from nltk.corpus import stopwords

def convert(input):
	"""
	Convert input from unicode to str
	"""
	if isinstance(input, dict):
		return {convert(key): convert(value) for key, value in input.iteritems()}
	elif isinstance(input, list):
		return [convert(element) for element in input]
	elif isinstance(input, unicode):
		return input.encode('utf-8')
	else:
		return input

#TODO: allow items without author or year. Come up with another method to compute key
def compute_key(item):
	authors = item['author'].split(' and ')

	tokens = ( [authors[0].split()[-1]] + 
		[author.split()[-1][0] for author in authors[1:]] + 
		[str(item['year'])] )

	key = ''.join(tokens).lower()
	return key

def fields_string(fields):
	assert( all( isinstance(item, basestring) for item in fields ) )
	result = ''.join(['(', ','.join(fields), ')'])
	return result

#TODO: fix this
def values_holder(fields):
	assert( all( isinstance(item, basestring) for item in fields ) )
	items = [":%s" % convert(item) for item in fields if convert(item) == item]
	result = ''.join(['(', ','.join(items), ')'])
	return result

_stops = stopwords.words('english')
def nice_tokens(s):
	if not isinstance(s, basestring):
		return [str(s)]

	tokens = [token.lower() for token in nltk.word_tokenize(s) 
		if 	token not in string.punctuation and 
			len(token) > 2 and
			'.' not in token and
			token not in _stops]
	return tokens		

#TODO: improve this
def is_close(s1, s2):
	return s1.lower() == s2.lower()







