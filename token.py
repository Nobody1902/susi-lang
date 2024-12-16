from enum import Enum
from error import Location

class TokenType(Enum):
    EOL = 0
    OPERATOR = 1
    VARIABLE = 2
    VALUE = 3
    IDENTIFIER = 4
    CLOSURE = 5
    IF = 6

class Token:

    def __init__(self, token_type: TokenType, value: any, location: Location) -> None:
        self.type = token_type
        self.value = value
        self.location = location

    def __str__(self):
        return f":({self.type.name}, {self.value})"

    def __repr__(self) -> str:
        if self.type == TokenType.EOL:
            return f":({self.type.name})"
        return f":({self.type.name}, {self.value})"


EOL_TOKEN = Token(TokenType.EOL, None, -1)
