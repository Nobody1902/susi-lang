import lexer
from interpreter import Interpreter
import error
from syntax import Syntax

syntax = Syntax("simple_syntax.json")

lex = lexer.Lexer(syntax)
# res = lex.parse("if(1 == 2)\n\t2 + 1\nelif(2 == 3)\n\t3 + 2\nelse\n\t4 + 3")
# res = lex.parse("2.2 - 0.2")
res = lex.parse("if(1 == 2)\n\ttrue\n\tfalse\nelif(3 == 4)\n\tfalse")
if type(res) == error.Error:
    print(res)
    exit()

res = lex.group(res)
if type(res) == error.Error:
    print(res)
    exit()

interpreter = Interpreter(syntax)
output = interpreter.run(res)
if type(output) == error.Error:
    print(output)
    exit()

for o in output:
    if o != None:
        print(o)
