import json
from os import name

class Operator:
    def __init__(self, name: str, sign: str, types: list[str] | None = None) -> None:
        self.name = name
        self.sign = sign
        self.types = types if types != None else []

    def __eq__(self, value: object, /) -> bool:
        return self.__str__().__eq__(value)
    
    def __str__(self) -> str:
        return self.name

class OperatorList(object):
    def __init__(self, operators: list[Operator]):
        self._operators = operators

    def __contains__(self, item):
        return self._operators.__contains__(item)

    def __iter__(self):
        for elem in self._operators:
            yield elem

    def __getitem__(self, key):
        if type(key) == int:
            return self._operators[key]

        return next((x for x in self._operators if x == key), None)

class Statement:
    def __init__(self, name: str, sign: str, condition: bool) -> None:
        self.name = name
        self.sign = sign
        self.condition = condition

    def __eq__(self, value: object, /) -> bool:
        return self.__str__().__eq__(value)
    
    def __str__(self) -> str:
        return self.name

    def __len__(self) -> int:
        return self.name.__len__()

    def __repr__(self) -> str:
        return self.name

class StatementList(object):
    def __init__(self, statements: list[Statement]):
        self._statements = statements

    def __contains__(self, item):
        return self._statements.__contains__(item)

    def __iter__(self):
        for elem in self._statements:
            yield elem

    def __getitem__(self, key):
        if type(key) == int:
            return self._statements[key]

        return next((x for x in self._statements if x == key), None)


class Syntax:
    def parse_operators(self, operators: dict) -> OperatorList:
        output = []
        for o in operators:
            types = operators[o]["types"] if "types" in operators[o] else None
            output.append(Operator(o, operators[o]["sign"], types))

        return OperatorList(output)

    def parse_statements(self, statements: dict) -> list[Statement]:
        output = []
        for s in statements:
            output.append(Statement(s, statements[s]["sign"], statements[s]["condition"]))

        return StatementList(output)
        

    def __init__(self, filepath: str) -> None:
        with open(filepath) as syntax:
            syntax_json = json.loads(syntax.read())

            self.keywords = syntax_json["keywords"]
            self.statements = self.parse_statements(syntax_json["statements"])
            self.operators = self.parse_operators(syntax_json["operators"])
            self.numbers = syntax_json["numbers"]
            self.closure = syntax_json["closure"]
            self.bool = syntax_json["bool"]

    
