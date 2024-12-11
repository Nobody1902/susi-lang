import json

class Syntax:
    def __init__(self, filepath: str) -> None:
        with open(filepath) as syntax:
            syntax_json = json.loads(syntax.read())

            self.keywords = syntax_json["keywords"]
            self.operators = syntax_json["operators"]
            self.numbers = syntax_json["numbers"]
            self.closure = syntax_json["closure"]

    
