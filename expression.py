from nltk import word_tokenize

def enum(*sequential):
	enums = dict( zip(sequential, range(len(sequential))) )
	return type('Enum', (), enums)

ExpressionType = enum('CLAUSE', 'AND', 'OR')

class S:
	def __init__(self, exptype, s1, s2):
		self.exptype = exptype
		self.s1 = s1
		self.s2 = s2

	def __str__(self):
		if self.exptype == ExpressionType.CLAUSE:
			return '%s=%s' % (self.s1, self.s2)

		elif self.exptype == ExpressionType.AND:
			return '(%s and %s)' % (self.s1, self.s2)

		elif self.exptype == ExpressionType.OR:
			return '(%s or %s)' % (self.s1, self.s2)

class Expression:
	def __init__(self, str_exp):
		self.tokens = word_tokenize( str_exp.replace('=', ' ') )
		self.stack = []
		self.parse(0)
		#print self.parsed
		#print self.to_cnf(self.parsed)

	def parse(self, idx):
		self.reduce()
		if idx == len(self.tokens):
			self.parsed =  self.stack.pop()
			return
		token = self.tokens[idx]

		if token == '(':
			self.stack.append(token)
			self.parse(idx + 1)

		elif token == ')':
			self.stack.pop(-2)
			self.parse(idx + 1)

		elif token in ['and', 'or']:
			self.stack.append(token)
			self.parse(idx + 1)

		else:
			s = S(ExpressionType.CLAUSE, token, self.tokens[idx+1])
			self.stack.append(s)
			self.parse(idx + 2)

	def reduce(self):
		if len(self.stack) < 3:
			return
		if not isinstance(self.stack[-1], S):
			return

		if self.stack[-2] == 'and':
			s = S(ExpressionType.AND, self.stack[-3], self.stack[-1])
			self.stack = self.stack[:-3] + [s]

		elif self.stack[-2] == 'or':
			s = S(ExpressionType.OR, self.stack[-3], self.stack[-1])
			self.stack = self.stack[:-3] + [s]

	def to_cnf(self, s = None):
		if not s:
			s = self.parsed

		if s.exptype == ExpressionType.CLAUSE:
			return [ [(s.s1, s.s2)] ]
		elif s.exptype == ExpressionType.AND:
			exp1 = self.to_cnf(s.s1)
			exp2 = self.to_cnf(s.s2)
			return exp1 + exp2
		elif s.exptype == ExpressionType.OR:
			exp1 = self.to_cnf(s.s1)	
			exp2 = self.to_cnf(s.s2)
			return [e1 + e2 for e1 in exp1 for e2 in exp2]

if __name__ == '__main__':
	s = '(author = son and author = han)or((year=1992 and title=abc) or author = gupta)'
	exp = Expression(s)
