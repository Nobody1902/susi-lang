import lexer
from interpreter import Interpreter
import error
from syntax import Syntax

syntax = Syntax("simple_syntax.json")

lex = lexer.Lexer(syntax)
res = lex.parse("var test = 2 * -3\nvar x = (test + test) * -3\ntest - x")
if type(res) == error.Error:
    print(res)
    exit()

res = lex.group(res)
if type(res) == error.Error:
    print(res)
    exit()

interpreter = Interpreter(syntax)
output = interpreter.run(res)
for o in output:
    if o:
        print(o)
