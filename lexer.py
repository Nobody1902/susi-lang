from os import stat
from token import Token, TokenType, EOL_TOKEN
from syntax import Statement, Syntax
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
                return Token(TokenType.VALUE, {"type": "int" if type(num) == int else "float", "value": num}, self.location.new())
            else:
                break


        return None

    def parse_variables(self, word: str, line: str, start: int) -> Token | None | error.Error:
        if(word != self.SYNTAX.keywords["var"]):
            return None
        
        line = line[start+1:]

        name = line[:line.find(self.SYNTAX.operators["="].sign)-1]
        value = line[line.find(self.SYNTAX.operators["="].sign)+2:]

        self.location.char += len(name) + 3 

        if(len(value) == 0 or len(name) == 0) or " " in name or line[line.find(self.SYNTAX.operators["="].sign)+1] != " " or line[line.find(self.SYNTAX.operators["="].sign)-1] != " ":
            return error.Error(f"Variable defined incorrectly: 'var {line.replace('\n', '')}'.", self.location)
        
        # Check if the variable name is a number
        is_num = self.parse_number(name)
        if(is_num != None):
            return error.Error(f"Variable name cannot be a number: '{name}'", self.location)
        
        # Check if the variable name is an operator
        for n in name:
            if(n in self.SYNTAX.operators):
                return error.Error(f"Variable name cannot be an operator: '{name}'", self.location)

        # Check if the variable name is a keyword
        if(name in self.SYNTAX.keywords.values()):
            return error.Error(f"Variable name cannot be a keyword: '{name}'", self.location)

        if(name in self.variables):
            return error.Error(f"Variable '{name}' has been already defined.", self.location)

        parsed = self.parse_line(value, check_multiline=False, start_char=self.location.new().char)

        if type(parsed) == error.Error:
            return parsed

        return Token(TokenType.VARIABLE, {"name": name, "value": parsed}, self.location.new())

    
    def parse_closure(self, i_line: str, start: int) -> tuple[Token, int] | None | error.Error:
        line = i_line[start:]

        if not line.startswith(self.SYNTAX.closure["("]) or (start != 0 and i_line[start-1] != " "):
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
        parsed = self.parse_line(value, check_multiline=False, start_char=self.location.char)
        if type(parsed) == error.Error:
            parsed.location.char -= 1
            return parsed

        return (Token(TokenType.CLOSURE, parsed, parsed[0].location), closing_idx)

    def parse_statment(self, token_list: list[str], statement: Statement):
        condition = None
        if not statement.sign in token_list and not statement.condition:
            return None
        elif statement.condition:
            for i, t in enumerate(token_list):
                if t.startswith(statement.sign + self.SYNTAX.keywords["if("]) and t.endswith(self.SYNTAX.keywords["if)"]):
                    condition = t[len(statement.sign):]
                    token_list[i] = t[:len(statement.sign)]
                    break
            else:
                return None


        split_idx = token_list.index(statement.sign)

        before = token_list[:split_idx]
        after = token_list[split_idx+1:]

        print(before, after)

        return (condition, before, after)

    def parse_if(self, line: str, i: int, st: int = 0, st_count: int = 3) -> tuple[Token] | None | error.Error:
        if not line[:i].startswith(self.SYNTAX.statements[st].sign):
            return None

        tabbed_split = line.replace("\n", "").split("\t")
        print(tabbed_split)

        prev_value = tabbed_split

        result = {}
        
        for i in range(st_count - st):
            res = self.parse_statment(prev_value, self.SYNTAX.statements[st+i])
            if res != None:
                stat_condition, preceding_value, stat_value = res
                result[stat_condition] = (preceding_value, stat_value)
                prev_value = preceding_value
            else:
                # Haven't found the statement sign
                continue

        print(f"{result=}")

        
        return None

    def parse_line(self, line:str, check_multiline = True, start_char=0) -> list[Token] | error.Error:
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
            
            # Find statements
            if check_multiline:
                statement = self.parse_if(line, i)
                if type(statement) == error.Error:
                    return statement

                if statement != None:
                    tokens.append(statement)
                    word = ""
                    break
            
            # Find numbers
            num = self.parse_number(word)
            if type(num) == error.Error:
                return num
                
            if num != None:
                tokens.append(num)
                word = ""
                continue
            
            # Find bools
            if word == self.SYNTAX.bool["true"]:
                tokens.append(Token(TokenType.VALUE, {"type": "bool", "value": True}, self.location.new()))
                word = ""
                continue

            if word == self.SYNTAX.bool["false"]:
                tokens.append(Token(TokenType.VALUE, {"type": "bool", "value": False}, self.location.new()))
                word = ""
                continue
            
            # Find operators
            if word in self.SYNTAX.operators:
                tokens.append(Token(TokenType.OPERATOR, word, self.location.new()))
                word = ""
                continue

            # Find variables
            if check_multiline:
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

    def format_newlines(self, code: str) -> str:
        output = ""
        statements = list(self.SYNTAX.statements)
        statements.sort(key=len)
        statements.reverse()

        lines = code.splitlines(keepends=True)
        skip = 0

        for l, line in enumerate(lines):
            if skip > 0:
                skip -= 1
                continue

            for s in statements:
                if line.startswith(str(s)):
                    break
            else:
                output += line
                continue

            # Multiline run conditions
            if l > 0 and output[l - 1][-1] != "\t":
                    output += "\t"           
            output += line.replace("\n", "")
            i = l
            while len(lines) - 1 > i:
                if lines[i + 1].startswith("\t"):
                    output += lines[i + 1].replace("\n", "")
                    skip += 1
                else:
                    break

                i += 1
                
        
        return output


    def parse(self, code: str, check_variables = True) -> list[Token] | error.Error:
        self.location.line = 0
        self.location.char = 0
        tokens = []
        
        code = self.format_newlines(code) 
        print(code)
                
        for line in code.splitlines(keepends=True):
            parsed_line = self.parse_line(line, check_multiline=check_variables)
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

                if not prev.value["type"] in self.SYNTAX.operators[t.value].types:
                    return error.Error(f"Operation '{t.value}' doesn't support type '{prev.value['type']}'", t.location)
                if not next.value["type"] in self.SYNTAX.operators[t.value].types:
                    return error.Error(f"Operation '{t.value}' doesn't support type '{next.value['type']}'", t.location)

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


