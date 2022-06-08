import { readFile } from "fs";

String.prototype.isalpha = function() {
    return 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'.includes(this[0]);
} 

String.prototype.isnumeric = function() {
    return '1234567890'.includes(this[0]);
}

// PQ.pq
const TokenType = Object.freeze({	
    // Parenthesis
    LeftParen: 0,
    RightParen: 1,
    // Brackets
    LeftCurlyBracket: 2,
    RightCurlyBracket: 3,
    LeftAngleBracket: 4,
    RightAngleBracket: 5,
	// BinaryOperators
    BinPlus: 6,
    BinMinus: 7,
    BinMultiply: 8,
    BinDivide: 9,
    BinPercent: 10,
    BinGreaterThan: 11,
    BinLessThan: 12,
    BinEquals: 13,
	// ETC
    Accessor: 14,
    Seperator: 15,
    Assign: 16,
    Declerator: 17,
    Keyword: 18,
    Number: 19,
    String: 20,
    Comment: 21,
    EOF: 22,
});

class Token {
    constructor(type, position, value) {
        this.type = type;
		this.position = position;
		if (value) this.value = value;
    }

    print() {
        const keys = Object.keys(TokenType);
        let str = `${keys[this.type]}`.padEnd(28)
		str += `(${this.position[0]}, ${this.position[1]})`.padEnd(10)
		if (this.value) {
			if (typeof this.value == 'number') str += `${this.value}`;
            else str += `"${this.value}"`;
        }
		console.log(str);
    }
}

// Lexer
class Lexer {
    constructor(src) {
        this.src = src
        this.cursor = 0
        this.col = 0
        this.row = 0
    }

    error(reason, pos) {
        throw Error(`${reason} (_:${pos[1]}:${pos[0]})`);
    }

	// Data Functions
    current() {
        return this.src[this.cursor];
    }

    peek(num = 1) {
        return this.src[this.cursor + num];
    }

    advance(amount = 1) {
        this.col += amount;
        this.cursor += amount;
    }

    // Lex Functions
	consume_space() {
		this.advance();
    }
		
	consume_newline() {
        this.col = 0;
		this.row += 1;
		this.cursor += 1;
    }
		
	consume_tab() {
        this.col += 4;
		this.cursor += 1;
    }

    lex_binary_operator(tokens) {
		const pos = [this.row, this.col];
		let type;
		if (this.current() == '+') type = TokenType.BinPlus;
		else if (this.current() == '-') type = TokenType.BinMinus;
		else if (this.current() == '/') type = TokenType.BinDivide;
		else if (this.current() == '*') type = TokenType.BinMultiply;			
		else if (this.current() == '%') type = TokenType.BinPercent;
		else if (this.current() == '>') type = TokenType.BinGreaterThan;		
		else if (this.current() == '<') type = TokenType.BinLessThan;
		this.advance();
		tokens.push(new Token(type, pos));
    }

    lex_binary_equals(tokens) {
		const pos = [this.row, this.col];
		this.advance(2);
		tokens.push(new Token(TokenType.BinEquals, pos));
    }

    lex_brackets(tokens) {
		const pos = [this.row, this.col];
		let type;
		if (this.current() == '{') type = TokenType.LeftCurlyBracket
		else if (this.current() == '}') type = TokenType.RightCurlyBracket
		else if (this.current() == '[') type = TokenType.LeftAngleBracket
		else if (this.current() == ']') type = TokenType.RightAngleBracket
		else if (this.current() == '(') type = TokenType.LeftParen
		else if (this.current() == ')') type = TokenType.RightParen
		this.advance();
		tokens.push(new Token(type, pos));
    }

    lex_etc(tokens) {
		const pos = [this.row, this.col];
		let type;
		if (this.current() == '.') type = TokenType.Accessor;
		else if (',;'.includes(this.current())) type = TokenType.Seperator;
		else if (this.current() == '=') type = TokenType.Assign;
		this.advance();
		tokens.push(new Token(type, pos));
    }

    lex_comment(tokens) {
        const pos = [this.row, this.col];
        this.advance(2); // skip both /
        let comment = '';
        while (this.current() && !(this.current() == '\n')) {
            comment += this.current();
            this.advance();
        }
        tokens.push(new Token(TokenType.Comment, pos, comment.trimStart()))
    }

    lex_string(tokens) {
		const pos = [this.row, this.col];
		let string = ''
		this.advance(2); // skip " '
		while (this.current() && !("\"'".includes(this.current()))) {
			string += this.current();
			this.advance();
        }
		if (!this.current()) 
			this.error("Unclosed string literal", pos);
		this.advance(2); // skip " '
		tokens.push(new Token(TokenType.String, pos, string));
    }

    lex_keyword(tokens) {
		const pos = [this.row, this.col];
		let keyword = '';
		while (this.current()) {
			// TODO: Find a better way to do this, this is just straight hacky
			if (' \n\t{}[]();+-*%/.,'.includes(this.current()))
				break;
			keyword += this.current();
			this.advance();
        }
		let type = TokenType.Keyword;
		if (keyword == 'let') type = TokenType.Declerator;
		else if (keyword == 'function') type = TokenType.Declerator;
		tokens.push(new Token(type, pos, keyword));
    }

    lex_numbers(tokens) {
		const pos = [this.row, this.col];
		let dots = 0;
		let num_str = '';
		while (this.current()) {
			if (!(this.current().isnumeric()) && !(this.current() == '.'))
				break;
			if (this.current() == '.')
				dots += 1;
			num_str += this.current();
			this.advance();
        }
		if (dots > 1) 
			this.error('Numbers can only contain one decimal', pos);
		tokens.push(new Token(TokenType.Number, pos, Number(num_str)));
    }

    run() {
        const tokens = [];
        while (this.current()) {
            // Spaces
			if (this.current() == ' ') {
				this.consume_space();
				continue;
            }

            // New Lines
			if (this.current() == '\n') {
				this.consume_newline();
				continue;
            }

            // Tabs
			if (this.current() == '\t') {
				this.consume_tab();
				continue;
            }

            // Binary Operators
			if ('+-/*%><'.includes(this.current())) {
				this.lex_binary_operator(tokens);
				continue;
            }
				
			if (this.current() == '=' && this.peek(1) == '=') {
				this.lex_binary_equals(tokens);
				continue;
            }

            // Brackets
			if ('{}[]()'.includes(this.current())) {
				this.lex_brackets(tokens);
				continue;
            }

			// ETC
			if ('.,=;'.includes(this.current())) {
				this.lex_etc(tokens);
				continue;
            }

            // Keywords
			if (this.current().isalpha()) {
				this.lex_keyword(tokens);
				continue;
            }
				
			// Numbers 
			if (this.current().isnumeric()) {
				this.lex_numbers(tokens);
				continue;
            }
				
			// Strings
			if ('\'"'.includes(this.current())) {
				this.lex_string(tokens);
				continue;
            }

            this.error(`Unknown token '${this.current()}'`, [this.row, this.col]);
        }
        tokens.push(new Token(TokenType.EOF, [this.row, this.col]));
        return tokens;
    }
}

// Main Code :)
function run(src) {
    const tokens = new Lexer(src).run();
    for (let token of tokens) {
        token.print();
    }
}

function usage() {
	console.log('Usage:');
	console.log('\tnode index.js [file-name].pq');
	console.log('');
	process.exit(0);
}

const args = process.argv.slice(2);
if (!(args.length > 0)) usage();
if (!(args[0].endsWith('.pq'))) { 
    console.log('You can only run files that end with \'.pq\'');
    process.exit(1);
}

try {
    readFile(args[0], function (err, data) {
        if (err) return console.error(err);
        const contents = data.toString();
        run(contents);
    });
} catch(error) {
    console.error(error);
}