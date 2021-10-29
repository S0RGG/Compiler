import pytest
from lexer import Lexer
from pyparser import Parser

def test_monster():
    pars = Parser(Lexer("tests/parser tests/request/monster.txt"))
    result = pars.parse().show_str()
    answer_file = open("tests/parser tests/response/monster.txt", 'r')
    answer = answer_file.read()
    answer_file.close()
    assert result == answer

if __name__ == '__main__':
    pytest.main()