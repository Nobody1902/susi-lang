from token import Token, TokenType, EOL_TOKEN
from typing import List
from syntax import Syntax
import error

class Lexer:
    def __init__(self, syntax: Syntax) -> None:
        self.SYNTAX = syntax
        self.location = error.Location(file="<main>", line=0)
        self.variables = []

    def parse_number(self, word: str) -> Token | error.Error | None:
        decimal_point: int = -1
        for i, char in enumerate(word):
            # Negative numbers
            if char == self.SYNTAX.numbers["-"]:
                if i != 0:
                    self.location.char -= 1
                    return error.Error(f"Unexpected '{self.SYNTAX.numbers['-']}'. Add spaces between numbers and operators.", self.location)
                continue
            # Decimal magic
            if char == self.SYNTAX.numbers["decimal"]:
                if i == 0 or decimal_point != -1:
                    # self.location.char -= i - 1
                    return error.Error(f"Unexpected '{self.SYNTAX.numbers['decimal']}'", self.location)
                decimal_point = i
                continue
            if char in self.SYNTAX.numbers.values():
                if i != len(word) - 1:
                    continue

                num = float(word) if decimal_point != -1 else int(word)
                return Token(TokenType.VALUE, num, self.location.new())
            else:
                break


        return None

    def parse_variables(self, word: str, line: str, start: int) -> Token | None | error.Error:
        if(word != self.SYNTAX.keywords["var"]):
            return None
        
        line = line[start+1:]

        ls = line.split(self.SYNTAX.operators["="])
        name = ls[0].replace(" ", "")
        value = ls[1][1:]

        self.location.char += len(name) + 3 

        if(len(ls) < 2 or len(name) == 0):
            return error.Error(f"Variable defined incorrectly: '{ls}'.", self.location)
        
        # Check if the variable name is a number
        is_num = self.parse_number(name)
        if(is_num != None):
            return error.Error(f"Variable name cannot be a number: '{name}'", self.location)
        
        # Check if the variable name is an operator
        for n in name:
            if(n in self.SYNTAX.operators.values()):
                return error.Error(f"Variable name cannot be an operator: '{name}'", self.location)

        # Check if the variable name is a keyword
        if(name in self.SYNTAX.keywords.values()):
            return error.Error(f"Variable name cannot be a keyword: '{name}'", self.location)

        if(name in self.variables):
            return error.Error(f"Variable '{name}' has been already defined.", self.location)

        parsed = self.parse_line(value, check_variables=False, start_char=self.location.new().char)

        if type(parsed) == error.Error:
            return parsed

        return Token(TokenType.VARIABLE, {"name": name, "value": parsed}, self.location.new())

    
    def parse_closure(self, line: str, start: int) -> tuple[Token, int] | None | error.Error:
        # Fix the location when a closure is inside the closure
        line = line[start:]

        if not line.startswith(self.SYNTAX.closure["("]):
            return None
        
        # Slicing magic
        reverse = line[::-1]
        try:
            reverse_idx = reverse.index(self.SYNTAX.closure[")"])
        except:
            self.location.char += 1
            return error.Error(f'Expected \'{self.SYNTAX.closure[")"]}\'', self.location.new())

        closing_idx = len(line) - reverse_idx

        value = line[1:closing_idx-1]
        parsed = self.parse_line(value, check_variables=False, start_char=self.location.char)
        if type(parsed) == error.Error:
            parsed.location.char -= 1
            return parsed

        return (Token(TokenType.CLOSURE, parsed, parsed[0].location), closing_idx)

    def parse_line(self, line:str, check_variables = True, start_char=0) ->List[Token] | error.Error:
        tokens = []
        word: str = ""

        if not line.endswith("\n"):
            line += "\n"

        self.location.char = start_char

        skip = 0
        for i, c in enumerate(line):
            
            self.location.nextchar()

            # FIXME: Skip chars for closures
            if skip > 0:
                skip-=1
                continue
                
            # Detect a closure
            closure = self.parse_closure(line, i)
            if type(closure) == error.Error:
                return closure

            if closure != None:
                tokens.append(closure[0])
                skip = closure[1]
                continue
            
            # Detect the end of the word
            if c != ' ' and c != '\n':
                word += c
                continue

            # Find numbers
            num = self.parse_number(word)
            if(type(num) == error.Error):
                return num
                
            if(num != None): 
                tokens.append(num)
                word = ""
                continue
                
            # Find operators
            if word in self.SYNTAX.operators.values():
                tokens.append(Token(TokenType.OPERATOR, word, self.location.new()))
                word = ""
                continue

            # Find variables
            if check_variables:
                var = self.parse_variables(word, line, i)
                if(type(var) == error.Error):
                    return var

                if(var != None):
                    self.variables.append(var.value["name"])
                    tokens.append(var)
                    word = ""
                    break
                    
            # Find identifiers of declared variables
            if word in self.variables:
                tokens.append(Token(TokenType.IDENTIFIER, word, self.location.new()))
                word = ""
                continue 
            
            if word.isspace():
                continue

            return error.Error(f"Undefined token: '{word}'", self.location)

        return tokens


    def parse(self, code: str, check_variables = True) -> list[Token] | error.Error:
        self.location.line = 0
        self.location.char = 0
        tokens = []
        
        print(code)
                
        for line in code.splitlines(keepends=True):
            parsed_line = self.parse_line(line, check_variables=check_variables)
            if type(parsed_line) == error.Error:
                return parsed_line

            tokens += parsed_line
            tokens.append(EOL_TOKEN)
            self.location.nextline()

        return tokens

    def group_operations(self, tokens: list[Token], operators: list[str]) -> list[Token] | error.Error:
        i = 0
        while i < len(tokens):
            t = tokens[i]

            if t.type == TokenType.OPERATOR and t.value in operators:
                if tokens[i-1].type == TokenType.EOL:
                    return error.Error(f"Couldn't find left side in operation '{t.value}'", t.location)
                if tokens[i+1].type == TokenType.EOL:
                    return error.Error(f"Couldn't find right side in operation '{t.value}'", t.location)

                prev = tokens[i-1]
                next = tokens[i+1]

                tokens.pop(i+1)
                tokens.pop(i-1)
                i -= 1

                tokens[i] = Token(TokenType.CLOSURE, [prev, t, next], prev.location)
            
            i += 1
        
        return tokens

    def group(self, tokens: list[Token]) -> list[Token] | error.Error:
        
        # First group values of closures and variables
        for t in tokens:
            if t.type == TokenType.VARIABLE or t.type == TokenType.CLOSURE:
                if type(t.value) == dict:
                    ret = self.group(t.value["value"])
                    if type(ret) == error.Error:
                        return ret
                    t.value["value"] = ret
        
        # Skip grouping operations
        if len(tokens) < 4:
            return tokens

        # Multiplication and division
        ret = self.group_operations(tokens, [self.SYNTAX.operators["*"], self.SYNTAX.operators["/"]])
        if type(ret) == error.Error:
            return ret

        # Addition and subtraction
        ret = self.group_operations(tokens, [self.SYNTAX.operators["+"], self.SYNTAX.operators["-"]])
        if type(ret) == error.Error:
            return ret

        return tokens


