
class Location:
    def __init__(self, file:str, line: int, char: int = -1) -> None:
        self.file = file
        self.line = line
        self.char = char

    def new(self):
        return Location(self.file, self.line, self.char)
    
    def __repr__(self) -> str:
        return f"('{self.file}', {self.line}" + f":{self.char})" if self.char != -1 else ")"

    def __add__(self, o):
        return Location(self.file, self.line, self.char + o.char)

    def nextline(self) -> None:
        self.line += 1
        self.char = 0

    def nextchar(self) -> None:
        self.char += 1

RUNTIME_LOCATION = Location("<RUNTIME>", -1, -1)

class Error:
  def __init__(self, value: str, location: Location) -> None:
    self.value = value
    self.location = location
    self.location.char-=1
    # self.location.nextchar()

  def __repr__(self) -> str:
    return f"Error at {self.location} -> {self.value}"
