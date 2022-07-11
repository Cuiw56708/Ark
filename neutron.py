

TN_INT = "INT"
TN_DEC = "DEC"
TN_PLUS = "PLUS"
TN_MINUS = "MINUS"
TN_MUL = "MUL"
TN_DIV = "DIV"
TN_RPAREN = "RPAREN"
TN_LPAREN = "LPAREN"

DIGITS = "0123456789"

FILENAME = ""
TEXT = ""



def run (filename, text):
    util = Util(filename, text)
    lex = Lexer(filename, text)
    tokens, error = lex.tokens()

    if error :return None, error

    parser = Parser(tokens)
    abstract_syntax_tree = parser.parse()
    
    return abstract_syntax_tree, None

def arrow(text, poss, pose):
    result = ''
    start = max(text.rfind('\n', 0, poss.index), 0)
    end = text.find('\n', start + 1)
    if end < 0: end = len(text)
    count = pose.line - poss.line + 1
    for i in range(count):
        line = text[start:end]
        cols = poss.col if i == 0 else 0
        cole = pose.col if i == count - 1 else len(line) - 1
        result += line + '\n'
        result += ' ' * cols + '^' * (cole - cols)
        start = end
        end = text.find('\n', start + 1)
        if end < 0: end = len(text)

    return result.replace('\t', '')


class Token:
    def __init__(self, type, value=None, start=None, end=None) -> None:
        self.type = type
        self.value = value

        if start: 
            self.start = start.clone()
            self.end = start.clone()
            self.end.step()
        if end : self.end = end
    def __repr__(self) -> str:
        if self.value :
            return f"{self.type}:{self.value}"
        return f"{self.type}"

class Lexer :
    def __init__(self, name, text) -> None:
        self.text = text
        self.filename = name
        self.position = Position(-1, 0, -1, name, text)
        self.current = None
        self.step()
    
    def step(self):
        self.position.step(self.current)
        self.current = self.text[self.position.index] if self.position.index < len(self.text) else None

    def tokens(self):
        tokens = []
        while self.current != None:
            if self.current in " \t":
                self.step()
            elif self.current in DIGITS:
                tokens.append(self.numbers())
            elif self.current == "+":
                tokens.append(Token(TN_PLUS, start=self.position))
                self.step()
            elif self.current == "-":
                tokens.append(Token(TN_MINUS, start=self.position))
                self.step()
            elif self.current == "*":
                tokens.append(Token(TN_MUL, start=self.position))
                self.step()
            elif self.current == "/":
                tokens.append(Token(TN_DIV, start=self.position))
                self.step()
            elif self.current == "(":
                tokens.append(Token(TN_LPAREN, start=self.position))
                self.step()
            elif self.current == ")":
                tokens.append(Token(TN_RPAREN, start=self.position))
                self.step()
            else:
                start = self.position.clone()
                char = self.current
                self.step()
                return [], CharIllegalError(start, self.position, "Illegal Character '"+char+"'")

        return tokens,None

    def numbers(self):
        numstr = ""
        dots = 0
        while self.current != None and self.current in DIGITS + ".":
            if self.current == ".":
                if dots == 1:
                    break
                dots += 1
                numstr += "."
            else:
                numstr += self.current
            self.step()
            
        if dots == 0:
            return Token(TN_INT, int(numstr), start=self.position )
        else:
            return Token(TN_DEC, float(numstr), start=self.position )

class Number:
    def __init__(self, token) -> None:
        self.token = token
    
    def __repr__(self):
        return f"{self.token}"
    
class Binary:
    def __init__(self, l, o, r) -> None:
        self.l = l
        self.o = o
        self.r = r

    def __repr__(self) -> str:
        return f"({self.l},{self.o},{self.r})"
class Response:
    def __init__(self) -> None:
        self.node = None
        self.error = None

    def response(self, result):
        if isinstance(result, Response):
            if result.error :self.error = result.error
            return result.node
        return result
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        self.error = error
        return self
    
class Parser:
    def __init__(self, tokens) -> None:
        self.current = None
        self.tokens = tokens
        self.index = -1
        self.step()
    def parse(self):
        result = self.expr()
        return result
    def step(self):
        self.index += 1
        if self.index < len(self.tokens):
            self.current = self.tokens[self.index]
        return self.current
    def expr(self):
        return self.operation(self.term, (TN_PLUS, TN_MINUS))
    def operation(self, get, operation_tokens):
        l = get()

        while self.current.type in operation_tokens:
            o = self.current
            self.step()
            r = get()
            l = Binary(l, o, r)
        
        return l
        
    def term(self):
        return self.operation(self.element, (TN_MUL, TN_DIV))
    def element(self):
        response = Response()
        token = self.current

        if token.type in (TN_INT, TN_DEC):
            response.response(self.step())
            return response.success(Number(token))

        return response.failure(TypeError(token.start, token.end, "Expected type 'int' or 'dec' "))

class Position:
    def __init__(self, index, line, col, name, text) -> None:
        self.name = name
        self.text = text
        self.index = index
        self.line = line
        self.col = col

    def step(self, current):
        self.index += 1
        self.col += 1
        
        if current == "\n":
            self.line += 1
            self.col = 0
        return self
    
    def clone(self):
        return Position(self.index, self.line, self.col, self.name, self.text)

class Error:
    def __init__(self, start , end, name, description) -> None:
        self.end = end
        self.start = start
        self.name = name
        self.description = description
    def __repr__(self) -> str:
        result = f"""{self.name}: {self.description}
    File {self.start.name}, at line {self.start.line+1}

    """+arrow(self.start.text, self.start, self.end)

        return result
class IllegalError(Error):
    def __init__(self, start, end, name, description) -> None:
        super().__init__(start, end, name, description)

class TypeError(Error):
    def __init__(self, start, end, description) -> None:
        self.start = start
        self.end = end

        super().__init__(start, end, "TypeError", description)

class SyntaxIllegalError(IllegalError):
    def __init__(self, start, end, description) -> None:
        self.start = start
        self.end = end

        super().__init__(start, end, "SyntaxIllegalError", description)

class CharIllegalError(IllegalError):
    def __init__(self, start, end, description) -> None:
        self.start = start
        self.end = end

        super().__init__(start, end, "CharIllegalError", description)
      
class Util:
    def __init__(self, name, text) -> None:
        pass
  
    

