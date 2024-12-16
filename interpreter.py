import error
from syntax import Syntax
from token import Token, TokenType

class Interpreter:

    def __init__(self, syntax: Syntax) -> None:
        self.variables = {}
        self.SYNTAX = syntax

    def split_lines(self, a: list[Token]):
        result = []
        start = 0 

        for i, value in enumerate(a):
            if value.type == TokenType.EOL:
      
                result.append(a[start:i])  
        
                start = i + 1  

        if start < len(a):
            result.append(a[start:])

        return result

    def run(self, tokens: list[Token]) -> list[any]:
        split = self.split_lines(tokens)
        output = []
        for i, line in enumerate(split):
            out = self.run_line(line)
            if type(out) == error.Error:
                out.location.line = i
                return out

            output.append(out)

        return output

    def run_operation(self, left: Token, right: Token, operation: str) -> any:
        print(f"{left.value} {operation} {right.value}")

    def run_closure(self, closure: Token) -> any:
        res = self.run_line(closure.value)
        if type(res) == error.Error:
            return res

        return Token(TokenType.VALUE, res, closure.location)

    def run_line(self, tokens: list[Token]) -> any:

        if len(tokens) == 1:
            tok = tokens[0]

            if tok.type != TokenType.CLOSURE and tok.type != TokenType.VARIABLE:
                if tok.type == TokenType.IDENTIFIER:
                    return self.variables[tok.value]

                return tok.value

            if tok.type == TokenType.CLOSURE:
                res = self.run_closure(tok)
                return res if type(res) == error.Error else res.value

            elif tok.type == TokenType.VARIABLE:
                res = self.run_closure(Token(TokenType.CLOSURE, tok.value["value"], tok.location))
                if type(res) == error.Error:
                    return res
                self.variables[tok.value["name"]] = res.value
            else:
                return error.Error(f"Token isn't a closure: {tok}", error.RUNTIME_LOCATION)
            return

        if len(tokens) == 3:
            left = tokens[0]
            operation = tokens[1]
            right = tokens[2]

            if operation.type != TokenType.OPERATOR:
                return error.Error(f"Expected an operator: {operation}", error.RUNTIME_LOCATION)
            if left.type == TokenType.CLOSURE:
                left = self.run_closure(left)
                if type(left) == error.Error:
                    return left

            if right.type == TokenType.CLOSURE:
                right = self.run_closure(right)
                if type(right) == error.Error:
                    return right

            if left.type == TokenType.IDENTIFIER:
                left = Token(TokenType.VALUE, self.variables[left.value], left.location)
            
            if right.type == TokenType.IDENTIFIER:
                right = Token(TokenType.VALUE, self.variables[right.value], right.location)

            op = operation.value
            if op == self.SYNTAX.operators["=="]:
                return {"type": bool, "value": right.value == left.value}

            # Number operations
            if op == self.SYNTAX.operators["+"]:
                return {"type": left.value["type"], "value": right.value["value"] + left.value["value"]}
            if op == self.SYNTAX.operators["-"]:
                return {"type": left.value["type"], "value": right.value["value"] - left.value["value"]}
            if op == self.SYNTAX.operators["*"]:
                return {"type": left.value["type"], "value": right.value["value"] * left.value["value"]}
            if op == self.SYNTAX.operators["/"]:
                return {"type": left.value["type"], "value": right.value["value"] / left.value["value"]}

            return error.Error(f"Unknown operation: {operation}", error.RUNTIME_LOCATION)

        return error.Error(f"Invaild tokens: {tokens}", error.RUNTIME_LOCATION)
