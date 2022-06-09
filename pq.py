import enum, sys

Position = (int, int)

# add _ & ^ $ # @ !
class TokenType(enum.Enum):
	# Parenthesis
	LeftParen = 0
	RightParen = 1
	# Brackets
	LeftCurlyBracket = 2
	RightCurlyBracket = 3
	LeftAngleBracket = 4
	RightAngleBracket = 5
	Plus = 6
	Minus = 7
	Asterisk = 8
	Backslash = 9
	Percent = 10
	GreaterThan = 11
	LessThan = 12
	DoubleEquals = 13
	Period = 14
	Comma = 15
	Equals = 16
	Semicolon = 17
	Underscore = 18
	And = 19
	Caret = 20
	Dollar = 21
	Hashtag = 22
	At = 23
	Exclamation = 24
	Declerator = 25
	Identifier = 26
	Number = 27
	String = 28
	Comment = 29
	EOF = 30

	def is_binary_op(self):
		return self in [	
			self.Plus,
			self.Minus,
			self.Asterisk,
			self.Backslash,
			self.Percent,
			self.GreaterThan,
			self.LessThan,
			self.DoubleEquals
		]

class Token():
	def __init__(self, type: TokenType, position: Position, value: str or int = None) -> None:
		self.type = type
		self.position = position
		self.value = value

	def __repr__(self) -> str:
		str = f"{self.type}".ljust(28)
		str += f"{self.position}".ljust(10)
		if not self.value is None:
			if isinstance(self.value, int): str += f"{self.value}"
			else: str += f"'{self.value}'"
		return str

# Lexer
class Lexer:
	def __init__(self, src: str):
		self.src = src
		self.cursor = 0
		self.col = 0
		self.row = 0

	def error(self, reason: str, pos: Position):
		raise Exception(f"{reason} (_:{pos[1]}:{pos[0]})")
		
	# Data Functions
	def current(self) -> str or None:
		try: return self.src[self.cursor]
		except: return None

	def peek(self, num: int) -> str or None:
		try: return self.src[self.cursor + num]
		except: return None

	def advance(self, amount: int = 1):
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
		
	def lex_binary_operator(self, tokens: list[Token]):
		pos = (self.row, self.col)
		type = None
		if self.current() == '+': type = TokenType.Plus
		elif self.current() == '-': type = TokenType.Minus
		elif self.current() == '/': type = TokenType.Backslash
		elif self.current() == '*': type = TokenType.Asterisk			
		elif self.current() == '%': type = TokenType.Percent
		elif self.current() == '>': type = TokenType.GreaterThan			
		elif self.current() == '<': type = TokenType.LessThan
		self.advance()
		tokens.append(Token(type, pos))

	def lex_binary_equals(self, tokens: list[Token]):
		pos = (self.row, self.col)
		self.advance(2)
		tokens.append(Token(TokenType.DoubleEquals, pos))

	def lex_brackets(self, tokens: list[Token]):
		pos = (self.row, self.col)
		type = None
		if self.current() == '{': type = TokenType.LeftCurlyBracket
		elif self.current() == '}': type = TokenType.RightCurlyBracket
		elif self.current() == '[': type = TokenType.LeftAngleBracket
		elif self.current() == ']': type = TokenType.RightAngleBracket
		elif self.current() == '(': type = TokenType.LeftParen
		elif self.current() == ')': type = TokenType.RightParen
		self.advance()
		tokens.append(Token(type, pos))

	def lex_etc(self, tokens: list[Token]):
		pos = (self.row, self.col)
		type = None
		if self.current() == '.': type = TokenType.Period
		elif self.current() in ',': type = TokenType.Comma
		elif self.current() in ';': type = TokenType.Semicolon
		elif self.current() == '=': type = TokenType.Equals
		elif self.current() in '_': type = TokenType.Underscore
		elif self.current() == '&': type = TokenType.And
		elif self.current() in '^': type = TokenType.Caret
		elif self.current() == '$': type = TokenType.Dollar
		elif self.current() == '#': type = TokenType.Hashtag
		elif self.current() == '@': type = TokenType.At
		elif self.current() == '!': type = TokenType.Exclamation
		self.advance()
		tokens.append(Token(type, pos))
	
	def lex_comment(self, tokens: list[Token]):
		pos = (self.row, self.col)
		self.advance(2) # skip both /
		comment = ''
		while not self.current() is None and not self.current() == '\n':
			comment += self.current()
			self.advance()
		tokens.append(Token(TokenType.Comment, pos, comment.lstrip()))

	def lex_string(self, tokens: list[Token]):
		pos = (self.row, self.col)
		string = ''
		self.advance(2) # skip " '
		while not self.current() is None and not self.current() in "\"'":
			string += self.current()
			self.advance()
		if self.current() is None: 
			self.error("Unclosed string literal", pos)
		self.advance(2) # skip " '
		tokens.append(Token(TokenType.String, pos, string))

	def lex_identifier(self, tokens: list[Token]):
		pos = (self.row, self.col)
		identifier = ''
		while not self.current() is None:
			# TODO: Find a better way to do this, this is just straight hacky
			if self.current() in ' \n\t{}[]();+-*%/.,=':
				break
			identifier += self.current()
			self.advance()
		type = TokenType.Identifier
		if identifier == 'let': type = TokenType.Declerator
		elif identifier == 'function': type = TokenType.Declerator
		elif identifier == 'class': type = TokenType.Declerator
		elif identifier == 'enum': type = TokenType.Declerator
		tokens.append(Token(type, pos, identifier))

	def lex_numbers(self, tokens: list[Token]):
		pos = (self.row, self.col)
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
		tokens.append(Token(TokenType.Number, pos, num))
		
	def run(self) -> list[Token]:
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
			if self.current() in '.,=;_&^$#@!':
				self.lex_etc(tokens)
				continue

			# Identifiers
			if self.current().isalpha():
				self.lex_identifier(tokens)
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

			self.error(f'Unknown token \'{self.current()}\'', (self.row, self.col))
		tokens.append(Token(TokenType.EOF, (self.row, self.col)))
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
