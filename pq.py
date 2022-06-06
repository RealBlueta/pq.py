import enum, sys

class TokenType(enum.Enum):
	# Parenthesis
	LeftParen = 0
	RightParen = 1
	# Brackets
	LeftCurlyBracket = 2
	RightCurlyBracket = 3
	LeftAngleBracket = 4
	RightAngleBracket = 5
	# BinaryOperators
	BinPlus = 6
	BinMinus = 7
	BinMultiply = 8
	BinDivide = 9
	BinPercent = 10
	BinGreaterThan = 11
	BinLessThan = 12
	BinEquals = 13
	# _?
	Semicolon = 14
	# ETC
	Accessor = 15
	Seperator = 16
	Assign = 17
	Declerator = 18
	Keyword = 19
	Number = 20
	String = 21
	Comment = 22
	EOF = 23

# Lexer
class Lexer:
	def __init__(self, src: str):
		self.src = src
		self.cursor = 0
		self.col = 0
		self.row = 0

	def error(self, reason, pos):
		raise Exception(f"{reason} (_:{pos[0]}:{pos[1]})")
		
	# Data Functions
	def current(self) -> str or None:
		try: return self.src[self.cursor]
		except: return None

	def peek(self, num: int) -> str or None:
		try: return self.src[self.cursor + num]
		except: return None

	def advance(self, amount=1):
		self.col += amount
		self.cursor += amount

	# Lex Functions
	def consume_space(self):
		self.advance()
		
	def consume_newline(self):
		self.col = 0
		self.row += 1
		self.cursor += 1	
		
	def consume_tab(self):
		self.col += 4
		self.cursor += 1
		
	def lex_binary_operator(self, tokens):
		pos = (self.col, self.row)
		type = None
		if self.current() == '+': type = TokenType.BinPlus
		elif self.current() == '-': type = TokenType.BinMinus
		elif self.current() == '/': type = TokenType.BinDivide
		elif self.current() == '*': type = TokenType.BinMultiply			
		elif self.current() == '%': type = TokenType.BinPercent
		elif self.current() == '>': type = TokenType.BinGreaterThan			
		elif self.current() == '<': type = TokenType.BinLessThan
		self.advance()
		tokens.append((type, pos))

	def lex_binary_equals(self, tokens):
		pos = (self.col, self.row)
		self.advance(2)
		tokens.append((TokenType.BinEquals, pos))

	def lex_brackets(self, tokens):
		pos = (self.col, self.row)
		type = None
		if self.current() == '{': type = TokenType.LeftCurlyBracket
		elif self.current() == '}': type = TokenType.RightCurlyBracket
		elif self.current() == '[': type = TokenType.LeftAngleBracket
		elif self.current() == ']': type = TokenType.RightAngleBracket
		elif self.current() == '(': type = TokenType.LeftParen
		elif self.current() == ')': type = TokenType.RightParen
		self.advance()
		tokens.append((type, pos))

	def lex_etc(self, tokens):
		pos = (self.col, self.row)
		type = None
		if self.current() == '.': type = TokenType.Accessor
		elif self.current() == ',': type = TokenType.Seperator
		elif self.current() == '=': type = TokenType.Assign
		elif self.current() == ';': type = TokenType.Semicolon
		self.advance()
		tokens.append((type, pos))
	
	def lex_comment(self, tokens):
		pos = (self.col, self.row)
		self.advance(2) # skip both /
		comment = ''
		while not self.current() is None and not self.current() == '\n':
			comment += self.current()
			self.advance()
		tokens.append((TokenType.Comment, pos, comment.lstrip()))

	def lex_string(self, tokens):
		pos = (self.col, self.row)
		string = ''
		self.advance(2) # skip " '
		while not self.current() is None and not self.current() in "\"'":
			string += self.current()
			self.advance()
		if self.current() is None: 
			self.error("Unclosed string literal", pos)
		self.advance(2) # skip " '
		tokens.append((TokenType.String, pos, string))

	def lex_keyword(self, tokens):
		pos = (self.col, self.row)
		keyword = ''
		while not self.current() is None:
			# TODO: Find a better way to do this, this is just straight hacky
			if self.current() in ' \n\t{}[]();+-*%/.,':
				break
			keyword += self.current()
			self.advance()
		type = TokenType.Keyword
		if keyword == 'let': type = TokenType.Declerator
		elif keyword == 'function': type = TokenType.Declerator
		tokens.append((type, pos, keyword))

	def lex_numbers(self, tokens):
		pos = (self.col, self.row)
		dots = 0
		num_str = ''
		while not self.current() is None:
			if not self.current().isnumeric() and not self.current() == '.':
				break
			if self.current() == '.':
				dots += 1
			num_str += self.current()
			self.advance()
		if dots > 1: 
			self.error('Numbers can only contain one decimal', pos)
		num = 0
		if dots > 0: num = float(num_str)
		else: num = int(num_str)
		tokens.append((TokenType.Number, pos, num))
		
	def run(self):
		tokens = []
		while not self.current() is None:
			# Spaces
			if self.current() == ' ':
				self.consume_space()
				continue
							
			# New Lines
			if self.current() == '\n':
				self.consume_newline()
				continue
				
			# Tabs
			if self.current() == '\t':
				self.consume_tab()
				continue
				
			# Binary Operators
			if self.current() in '+-/*%><':
				self.lex_binary_operator(tokens)
				continue
				
			if self.current() == '=' and self.peek(1) == '=':
				self.lex_binary_equals(tokens)
				continue
				
			# Brackets
			if self.current() in '{}[]()':
				self.lex_brackets(tokens)
				continue

			# ETC
			if self.current() in '.,=;':
				self.lex_etc(tokens)
				continue

			# Keywords
			if self.current().isalpha():
				self.lex_keyword(tokens)
				continue
				
			# Numbers
			if self.current().isnumeric():
				self.lex_numbers(tokens)
				continue
				
			# Strings
			if self.current() in "\"'":
				self.lex_string(tokens)
				continue
				
			# Comments
			if self.current() == '/' and self.peek(1) == '/':
				self.lex_comment(tokens)
				continue

			self.error(f'Unknown token \'{self.current()}\'', (self.col, self.row))
		tokens.append((TokenType.EOF, (self.col, self.row)))
		return tokens

# Main Code :)
def run(src: str):
	tokens = Lexer(src).run()
	for token in tokens:
		print(token)

def usage():
	print('Usage:')
	print(f'\t{sys.argv[0]} [file-name].pq')
	print('')
	sys.exit(0)
	
def main():
	args = sys.argv[1:]
	if not len(args) > 0: usage()
	if not args[0].endswith('.pq'): return print('You can only run files that end with \'.pq\'')
	try:
		with open(args[0]) as file:
			run(file.read())
	except Exception as err:
		print(err)

if __name__ == '__main__':
	main()	
