import sys
from collections import deque
from token import NEWLINE

class Lexem:
    def __init__(self, row, col, type, code=None, value=None):
        self.row, self.col, self.type, self.code, self.value = row, col, type, code, value
    
    def __repr__(self):
        return f"({self.row}, {self.col})\t{Lexer.PRESENTATION[self.type]}\t{self.code}\t{self.value}"
    
    def __str__(self):
        return f"({self.row}, {self.col})\t{Lexer.PRESENTATION[self.type]}\t{self.code}\t{self.value}"

class Lexer:
    def __init__(self, file):
        self.file = open(file, 'r')
        self.state = None
        self.current_char = None
        self.row, self.col = 1,0
        self.stack = deque()
        self.stack.append(0)
        self.current_dedent = 0
        self.indent_checked = False

    # types of lexemes
    INTNUMBER, FLOATNUMBER, IDENTIFIER, STRING,\
    IF, ELIF, ELSE, WHILE, FOR, DEF, IN, RETURN,\
    PRINT, RANGE, TRUE, FALSE,\
    SET, PLUS, MINUS, MULTIPLY, DIVISION, REMAINDER,\
    LRBRACKET, RRBRACKET, LSBRACKET, RSBRACKET,\
    INDENT, DEDENT, COMMA, COLON, LESS, GREATER, QUOTE1, QUOTE2, DECIMALPOINT, NEWLINE, EOF, BREAK = range(38)

    PRESENTATION = {
        INTNUMBER   : "integer",
        FLOATNUMBER : "float",
        IDENTIFIER  : "id",
        STRING      : "string",
        IF          : "if",
        ELIF        : "elif",
        ELSE        : "else",
        WHILE       : "while",
        FOR         : "for",
        DEF         : "def",
        IN          : "in",
        RETURN      : "return",
        PRINT       : "print",
        RANGE       : "range",
        TRUE        : "True",
        FALSE       : "False",
        SET         : "set",
        PLUS        : "plus",
        MINUS       : "minus",
        MULTIPLY    : "mult",
        DIVISION    : "div",
        REMAINDER   : "rem",
        LRBRACKET   : "lrbrack",
        RRBRACKET   : "rrbrack",
        LSBRACKET   : "lsbrack",
        RSBRACKET   : "rsbrack",
        INDENT      : "indent",
        DEDENT      : "dedent",
        COMMA       : "comma",
        COLON       : "colon",
        LESS        : "less",
        GREATER     : "greater",
        QUOTE1      : "quote1",
        QUOTE2      : "quote2",
        DECIMALPOINT: "point",
        NEWLINE     : "newline",
        EOF         : "EOF",
    }

    KEYWORDS = {
        'if'        : IF,
        'elif'      : ELIF,
        'else'      : ELSE,
        'while'     : WHILE,
        'for'       : FOR,
        'def'       : DEF,
        'in'        : IN,
        'return'    : RETURN,
        'break'     : BREAK,
    }

    RESERVEDNAMES = {
        'print'     : PRINT,
        'range'     : RANGE,
        'True'      : TRUE,
        'False'     : FALSE, 
    }

    SYMBOLS = {
        '='         : SET,
        '+'         : PLUS,
        '-'         : MINUS,
        '*'         : MULTIPLY,
        '/'         : DIVISION,
        '%'         : REMAINDER,
        '('         : LRBRACKET,
        ')'         : RRBRACKET,
        '['         : LSBRACKET,
        ']'         : RSBRACKET,
        ','         : COMMA,
        ':'         : COLON,
        '<'         : LESS,
        '>'         : GREATER,
        "'"         : QUOTE1,
        '"'         : QUOTE2,
        '.'         : DECIMALPOINT,
        '\n'        : NEWLINE,
    }

    def _string(self, quote):
        self.get_next_char()
        result = ""
        while self.current_char != quote:
            result += self.current_char
            self.get_next_char()
        self.get_next_char()
        return result

    def error(self, message):
        print(f"Lexer error: {message} in possition {self.row,self.col}")
        sys.exit(1)

    def get_next_char(self):
        if self.current_char == '\n':
            self.row += 1
            self.col = 0
        
        self.current_char = self.file.read(1)
        self.col += 1

    def get_next_token(self):
        self.state = None
        self.code = None
        self.value = ""
        while self.state == None:
            if self.current_char == None:
                self.get_next_char()
            # end of file
            if self.current_dedent > 0:
                self.current_dedent -= 1
                self.state = Lexer.DEDENT
                return Lexem(self.row, self.col, Lexer.DEDENT)
            elif len(self.current_char) == 0:
                if len(self.stack) > 1:
                    self.stack.pop()
                    self.state = Lexer.DEDENT
                    return Lexem(self.row, self.col, Lexer.DEDENT)
                self.state = Lexer.EOF
                self.code = "EOF"
                self.value = ""
                while 0 < self.stack[-1]:
                        self.stack.pop()
                        self.current_dedent += 1
            # comment
            elif self.current_char == '#':
                while self.current_char not in ['\n', '']:
                    self.get_next_char()
                if self.current_char == "\n":
                    self.get_next_char()
            # indent and dedent
            elif self.col == 1 and not self.indent_checked:
                self.indent_checked = True
                indent = ""
                while self.current_char == ' ':
                    indent += self.current_char
                    self.get_next_char()
                if self.current_char == '\n':
                    indent = ''
                elif len(indent) > self.stack[-1]:
                    self.state = Lexer.INDENT
                    self.code = indent
                    self.stack.append(len(indent))
                elif len(indent) < self.stack[-1]:
                    while len(indent) < self.stack[-1]:
                        self.stack.pop()
                        self.current_dedent += 1
                    if len(indent) != self.stack[-1]:
                        self.error("Invalid indentation")
                else:
                    return self.get_next_token()
            elif self.current_char == ' ':
                self.get_next_char()
            # string
            elif self.current_char in ["'", '"']:
                self.state = Lexer.STRING
                self.code = f"'{self._string(self.current_char)}'"
                self.value = eval(self.code)
            # symbols
            elif self.current_char in Lexer.SYMBOLS:
                self.state = Lexer.SYMBOLS[self.current_char]
                self.code = self.current_char
                self.get_next_char()
            # numbers float and integer
            elif self.current_char.isdigit():
                number = ""
                number += self.current_char
                self.get_next_char()
                while self.current_char.isdigit() or self.current_char == "_":
                    number += self.current_char
                    self.get_next_char()
                if self.current_char.isalpha():
                    self.error('Invalid identifier')
                try:
                    if number[-1] == "_" or number.index("__"):
                        self.error('Invalid decimal literal')
                except ValueError:
                    pass
                if self.current_char == '.':
                    number += '.'
                    self.get_next_char()
                    if self.current_char.isdigit():
                        number += self.current_char
                        self.get_next_char()
                    else:
                        self.error('Invalid decimal literal')
                    while self.current_char.isdigit() or self.current_char == "_":
                        number += self.current_char
                        self.get_next_char()
                    try:
                        if number[-1] == "_" or number.index("__"):
                            self.error('Invalid decimal literal')
                    except ValueError:
                        pass
                    self.state = Lexer.FLOATNUMBER
                else:
                    self.state = Lexer.INTNUMBER
                self.code = number
                self.value = eval(number)
            # identifiers, keywords and reserved names
            elif self.current_char.isalpha() or self.current_char == '_':
                identifier = ""
                while self.current_char.isalpha() or self.current_char.isdigit() or self.current_char == '_':
                    identifier += self.current_char
                    self.get_next_char()
                if identifier in Lexer.KEYWORDS:
                    self.state = Lexer.KEYWORDS[identifier]
                    self.code = identifier
                elif identifier in Lexer.RESERVEDNAMES:
                    self.state = Lexer.RESERVEDNAMES[identifier] 
                    self.code = identifier
                else:
                    self.state = Lexer.IDENTIFIER
                    self.code = identifier
            else:
                self.error(f'Unexpected symbol: {self.current_char}')
        self.indent_checked = False
        return Lexem(self.row, self.col, self.state, self.code, self.value)