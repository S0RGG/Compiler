import argparse
from lexer import Lexer
from pyparser import Parser 

argparser = argparse.ArgumentParser()
argparser.add_argument('-m', '--mode', action='store', help='select compilator mod: lexer | parser')
argparser.add_argument('-f', '--file', action='store', help='specify the path to the file')

flags = argparser.parse_args()

# DEBUG
# flags.mode = "parser"
# flags.file = "c:/Users/Ilcha/OneDrive/Рабочий стол/compiler-master/tests/lexer tests/request/if.txt"

match flags.mode:
    case "lexer":
        lex = Lexer(flags.file) #создаём лексер/передаём
        state = None
        while state != Lexer.EOF:
            print(lex.get_next_token())
            state = lex.state
    case "parser":
        pars = Parser(Lexer(flags.file))
        tree = pars.parse()
        print(tree, end='')
    case _:
        print("Wrong paramenter -m (--mode). Select compiler mode (-m parser | -m lexer)") 
if not flags.file:
    print("Wrong paramenter -f (--file). Select input file (-f FILE)")