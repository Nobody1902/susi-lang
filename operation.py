from token import Token, TokenType

class Operation:
    def __init__(self, left: Token, right: Token, operand: str):
        self.left = left
        self.right = right
        self.operand = operand
