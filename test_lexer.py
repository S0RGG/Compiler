import os
import pytest
from lexer import Lexer

base_path = "tests/lexer tests/"
files = os.listdir(base_path+"request")
@pytest.mark.parametrize(
    ('test_path'), [(test_name) for test_name in files]
)
def test_lexer(test_path):
    try:
        lex = Lexer(base_path+"request/"+test_path)
        result = ""
        state = None
        while state != Lexer.EOF:
            result += str(lex.get_next_token()) + '\n'
            state = lex.state
        answer_file = open(base_path+"response/"+test_path, 'r')
        answer = answer_file.read()
        answer_file.close()
        assert result == answer
    except:
        pass

if __name__ == '__main__':
    pytest.main()