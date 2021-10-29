import os
from lexer import Lexer
from pyparser import Parser

def answer_lexer(test_folder, file_name):
    try:
        lex = Lexer(test_folder+"request/"+file_name)
        result = ""
        state = None
        while state != Lexer.EOF:
            result += str(lex.get_next_token()) + '\n'
            state = lex.state
        answer_file = open(test_folder+"response/"+file_name, 'w', encoding='utf8')
        answer_file.write(result)
        answer_file.close()
    except SystemExit as e:
        pass

def answer_parser(test_folder, file_name):
    try:
        pars = Parser(Lexer(test_folder+"request/"+file_name))
        result = pars.parse().show_str()
        answer_file = open(test_folder+"response/"+file_name, 'w', encoding='utf8')
        answer_file.write(result)
        answer_file.close()
    except SystemExit as e:
        pass

test_folder = "tests/lexer tests/"
files = os.listdir(test_folder+"request")
for file_name in files:
    answer_lexer(test_folder, file_name)

test_folder = "tests/parser tests/"
files = os.listdir(test_folder+"request")
for file_name in files:
    answer_parser(test_folder, file_name)
