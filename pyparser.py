import sys
from lexer import Lexer

class Node:
    def __init__(self, pattern, value = None, childrens = []):
        self.pattern = pattern
        self.value = value
        self.childrens = childrens

    def show_str(self, level=0):
        str = ""
        if self.value != None:
            str += f"{Parser.PRESENTATION[self.pattern]} : {self.value}" + "\n"
        else:
            str += f"{Parser.PRESENTATION[self.pattern]}" + "\n"
        if self.childrens != []:
            for children in self.childrens:
                str += '|   '*level
                str += "|+-"
                if children.childrens != []:
                    str += children.show_str(level+1)
                else:
                    str += children.show_str(level)
        return str

    def __repr__(self):
        return self.show_str()

    def __str__(self):
        return self.show_str()
            
class Parser:
    # Nonterminals
    PROGRAM, LIST, MODIFICATION, FORMULA, FUNCTION, IDENTIFIER, FORMALPARAMETERS, FACTPARAMETERS,\
    ADD, SUB, SET, LESS, GREATER, MUL, DIV, REM,\
    IFCONSTRUCTION, ELIFCONSTRUCTION, ELSECONSTRUCTION, WHILECONSTRUCTION, FORCONSTRUCTION, DEFCONSTRUCTION, BLOCK,\
    INTNUMBER, FLOATNUMBER, STRING, RETURN, LISTELEMENT = range(28)

    PRESENTATION = {
        PROGRAM             : "PROGRAM",
        LIST                : "LIST",
        MODIFICATION        : "MODIFICATION",
        FORMULA             : "FORMULA",
        FUNCTION            : "FUNCTION",
        IDENTIFIER          : "IDENTIFIER",
        FORMALPARAMETERS    : "FORMALPARAMETERS",
        FACTPARAMETERS      : "FACTPARAMETERS",
        ADD                 : "ADD",
        SUB                 : "SUB",
        SET                 : "SET",
        MUL                 : "MUL",
        DIV                 : "DIV",
        REM                 : "REM",
        LESS                : "LESS",
        GREATER             : "GREATER",
        IFCONSTRUCTION      : "IFCONSTRUCTION",
        ELIFCONSTRUCTION    : "ELIFCONSTRUCTION",
        ELSECONSTRUCTION    : "ELSECONSTRUCTION",
        WHILECONSTRUCTION   : "WHILECONSTRUCTION",
        FORCONSTRUCTION     : "FORCONSTRUCTION",
        DEFCONSTRUCTION     : "DEFCONSTRUCTION",
        BLOCK               : "BLOCK",
        INTNUMBER           : "INTNUMBER",
        FLOATNUMBER         : "FLOATNUMBER",
        STRING              : "STRING",
        RETURN              : "RETURN",
        LISTELEMENT         : "LISTELEMENT"
    }

    def __init__(self, lex): 
        self.lex = lex
    
    def error(self, message):
        print(f"Parser error: {message} in possition {self.lex.row,self.lex.col}")
        sys.exit(1)

    def term(self):
        match self.lex.state:        
            case Lexer.IDENTIFIER:
                identifier = Node(Parser.IDENTIFIER, self.lex.code)
                self.lex.get_next_token()
                match self.lex.state:                          
                    case _: # identifier
                        return identifier
            case Lexer.INTNUMBER:
                node = Node(Parser.INTNUMBER, self.lex.code)
                self.lex.get_next_token()
                return node
            case Lexer.FLOATNUMBER:
                node = Node(Parser.FLOATNUMBER, self.lex.code)
                self.lex.get_next_token()
                return node
            case Lexer.STRING:
                node = Node(Parser.STRING, self.lex.code)
                self.lex.get_next_token()
                return node
            case Lexer.LRBRACKET:
                self.lex.get_next_token()
                formula = self.formula()
                if self.lex.state != Lexer.RRBRACKET:

                    self.error("Expected ')'")
                self.lex.get_next_token()
                return formula
            case _:
                self.error(f"Unexpected symbol")

    def product(self):
        left = self.term()
        match self.lex.state:
            case Lexer.MULTIPLY:
                self.lex.get_next_token()
                return Node(Parser.MUL, childrens=[left, self.product()])
            case (Lexer.DIVISION | Lexer.REMAINDER): # noncommutative operation with same priority
                while self.lex.state in [Lexer.DIVISION, Lexer.MULTIPLY, Lexer.REMAINDER]:
                    match self.lex.state:
                        case Lexer.DIVISION:
                            self.lex.get_next_token()
                            right = self.term()
                            left = Node(Parser.DIV, childrens=[left, right])
                        case Lexer.MULTIPLY:
                            self.lex.get_next_token()
                            right = self.term()
                            left = Node(Parser.MUL, childrens=[left, right])
                        case Lexer.REMAINDER:
                            self.lex.get_next_token()
                            right = self.term()
                            left = Node(Parser.REM, childrens=[left, right])
                return left
            case _:
                return left

    def sum(self):
        left = self.product()
        match self.lex.state:
            case Lexer.PLUS:
                self.lex.get_next_token()
                return Node(Parser.ADD, childrens=[left, self.sum()])
            case Lexer.MINUS: # noncommutative operation (1 - 2 - 3 и 1 + 1 - 1 + 1)
                while self.lex.state in [Lexer.MINUS, Lexer.PLUS]:
                    if self.lex.state == Lexer.MINUS:
                        self.lex.get_next_token()
                        right = self.product()
                        left = Node(Parser.SUB, childrens=[left, right])
                    else:
                        self.lex.get_next_token()
                        right = self.product()
                        left = Node(Parser.ADD, childrens=[left, right])
                return left
            case _:
                return left

    def formula(self):
        left = self.sum()
        match self.lex.state:
            case Lexer.LESS:
                self.lex.get_next_token()
                return Node(Parser.LESS, childrens=[left, self.formula()])
            case Lexer.GREATER:
                self.lex.get_next_token()
                return Node(Parser.GREATER, childrens=[left, self.formula()])
            case _:
                return left
    
    def block(self, depth=1):
        # if self.lex.state == Lexer.TABULATION:
        #     instructions = []
        #     # while self.lex.state == Lexer.TABULATION:
        #     #     self.lex.get_next_token()
        #     instructions += [self.instruction(depth)]
        # else:
        #     self.error("Expected indent")
        instructions = []
        indent_len = len(self.lex.code)
        while self.lex.state == Lexer.TABULATION:
            if indent_len == len(self.lex.code):
                for _ in range(depth):
                    if self.lex.state == Lexer.TABULATION:
                        self.lex.get_next_token()
                instructions += [self.instruction(depth)]
                while self.lex.state == Lexer.NEWLINE:
                    self.lex.get_next_token()
            else:
                self.error("Incorrect indent")
        return Node(Parser.BLOCK, childrens=instructions)

    def instruction(self, depth=0):
        match self.lex.state:
            # IF pattern (if FORMULA: \n BLOCK)
            case Lexer.IF:
                self.lex.get_next_token()
                statement = self.formula()
                if self.lex.state == Lexer.COLON:
                    self.lex.get_next_token()
                    if self.lex.state == Lexer.NEWLINE:
                        self.lex.get_next_token()
                        return Node(Parser.IFCONSTRUCTION, childrens=[statement, self.block(depth+1)])
                    else:
                        self.error("Expected new line")
                else:
                    self.error("Expected ':'")
            # WHILE pattern (while FORMULA: \n BLOCK)
            case Lexer.WHILE:
                self.lex.get_next_token()
                statement = self.formula()
                if self.lex.state == Lexer.COLON:
                    self.lex.get_next_token()
                    if self.lex.state == Lexer.NEWLINE:
                        self.lex.get_next_token()
                        return Node(Parser.WHILECONSTRUCTION, childrens=[statement, self.block(depth+1)])
                    else:
                        self.error("Expected new line")
                else:
                    self.error("Expected ':'")
            case _:
                return self.formula()

    # program is instructions list
    def program(self):
        instructions = []
        while self.lex.state != Lexer.EOF:
            while self.lex.state == Lexer.NEWLINE: # skip empty lines
                self.lex.get_next_token()
            instructions += [self.instruction()]
        return Node(Parser.PROGRAM, childrens=instructions)

    def parse(self):
        self.lex.get_next_token()
        return self.program()