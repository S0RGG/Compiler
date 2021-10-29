import os
import pytest
from lexer import Lexer
from pyparser import Parser

base_path = "tests/parser tests/"
files = os.listdir(base_path+"request")
@pytest.mark.parametrize(
    ('test_path'), [(test_name) for test_name in files]
)
def test_parser(test_path):
    try:
        pars = Parser(Lexer(base_path+"request/"+test_path))
        result = pars.parse().show_str()
        answer_file = open(base_path+"response/"+test_path, 'r')
        answer = answer_file.read()
        answer_file.close()
        print(result)
        assert result == answer
    except:
        pass

if __name__ == '__main__':
    pytest.main()