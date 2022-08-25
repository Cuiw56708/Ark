

import string
from types import NoneType


INT = "int"
DEC = "dec"
PLUS = "PLUS"
MINUS = "MINUS"
ID = "ID"
KW = "KEYWORD"
EQ = "EQ"
MUL = "MUL"
DIV = "DIV"
POWER = "POWER"
MOD = "MOD"
RPN = "RPN"
LPN = "LPN"

EE = "EE"
NE = "NE"
LT = "LT"
LTE = "LTE"
GT = "GT"
GTE = "GTE"

END = "END"

KEYWORD_DICT = {
    "variable_definition":"val",
    "boolean_true":"true",
    "boolaen_false":"false",
    "logical_and":"&&",
    "logical_not":"!",
    "logical_or":"||"
}

VAR_PTN = string.ascii_letters + "$"
DIGITS = "0123456789"

FILENAME = ""
TEXT = ""

imports = ""


def run (filename, text):
    """
        RUN THE CODE <text> using the <filename> file name.
        arguments:
        filename - file name of the code file
    """
    lex = Lexer(filename, text)
    tokens, error = lex.tokens()

    if error :
        return None, error

    parser = Parser(tokens)
    abstract_syntax_tree = parser.parse()

    cal = Calculator()
    context = Context("main")
    context.symbols = global_data
    
    if check(abstract_syntax_tree):
        return None, abstract_syntax_tree.error
    resp = cal.cal(abstract_syntax_tree.node, context)
    
    return resp, resp.error

def check(obj):
    if obj.error:
        return True
    return False
def arrow(text, poss, pose):
    """
        Show error arrows.
        arguments:
        text - the error text
        poss - start position
        pose - end position
    """
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

    return "\a" + result.replace("\t", "")
class Bool:
    # boolean
    def __init__(self, value) -> None:
        self.value = value
        self.setcontext()

    def clone(self):
        new = Digit(self.value)
        if type(self) == NoValue:
            new.locate()
            new.setcontext()
            return new
        new.locate(self.start, self.end)
        new.setcontext(self.context)
        return new

    def locate(self, start=None, end=None):
        self.start = start
        self.end = end
        return self

    def setcontext(self, context=None):
        self.context = context
        return self
        
    def equals(self, factor):
        if check(factor):
            if self.value == 0 and factor.value == 0 :
                return True
            elif self.value != 0 and factor.value != 0 :
                return False
    def not_equals(self, factor):
        if check(factor):
            if self.value == 0 and factor.value == 0 :
                return False
            elif self.value != 0 and factor.value != 0 :
                return False
            return True
    
    def and_op(self, factor):
        if check(factor):
            if self.value == 0 and factor.value == 0 :
                return True
            return False

    def or_op(self,factor):
        if self.value == 0 and factor.value == 0 :
            return True
        elif self.value != 0 and factor.value == 0 :
            return True
        elif self.value == 0 and factor.value != 0 :
            return True
        elif self.value != 0 and self.value != 0 :
            return False

    def check(self, obj):
        return isinstance(obj, Bool)
    
    def __repr__(self) -> str:
        if self.value == 0:
            return "true"
        return "false"

class Calculator:
    def cal(self, node, context):
        name = f"cal_{type(node).__name__}"
        fun = getattr(self, name, self.no)
        result = fun(node, context)
        return result
    
    def cal_VariableCreate(self, node, context):
        response = RuntimeResponse()
        key = node.name_token.value
        value = response.response(Calculator().cal(node.value, context))

        if check(response):
            return response
        BANNED = ["nov"]
        if key in BANNED :
            response.error = SyntaxIllegalException(node.start, node.end, f"Invalid Syntax of usage of keyword '{key}' ")
        if check(response):
            return response

        context.symbols.set(key, value)
        
        return response.success(value)

    def cal_VariableAccess(self, node, context):
        response = RuntimeResponse()
        key = node.name_token.value

        value = context.symbols.get(key)

        if not value:
            return response.failure(RuntimeException(node.start, node.end, "RuntimeException", f"{key} is not defined", context))
        
        value = value.clone().locate(node.start, node.end)

        return response.success(value)
    def cal_Number(self, node, context):
        return RuntimeResponse().success(Digit(node.token.value).setcontext(context).locate(node.start, node.end))

    def cal_Binary(self, node, context):
        response = RuntimeResponse()
        l = response.response(self.cal(node.l, context))
        if check(response):
            return response

        r = response.response(self.cal(node.r, context))
        if check(response):
            return response

        flag = False

        if node.o.type == PLUS:
            result, error = l.add(r)
        elif node.o.type == MINUS:
            result, error = l.minus(r)
        elif node.o.type == MUL:
            result, error = l.multiply(r)
        elif node.o.type == DIV:
            result, error = l.divide(r)
        elif node.o.type == POWER:
            result, error = l.power(r)
        
        elif node.o.type == MOD:
            result, error = l.modulo(r)
        else :
            flag = True

        if error and flag:
            return response.failure(error)
        if type(result) == NoneType :
            return response.failure(error)
        return response.success(result.locate(node.start, node.end))

    def cal_Unary(self, node, context):
        response = RuntimeResponse()
        result = response.response(self.cal(node.n, context))
        if check(response) :
            return response
        
        if node.o.type == MINUS:
            result, error = result.multiply(Digit(-1))
        if error :
            response.failure(error)
        return response.success(result.locate(node.start, node.end))

    def no(self, a, b):
        pass
class Context:
    def __init__(self, name, parent=None, parent_position=None) -> None:
        self.name = name
        self.parent = parent
        self.parent_position = parent_position
        self.symbols = DataTable()

class Digit:
    def __init__(self, value) -> None:
        self.value = value
        self.setcontext()

    def clone(self):
        new = Digit(self.value)
        if type(self) == NoValue:
            new.locate()
            new.setcontext()
            return new
        new.locate(self.start, self.end)
        new.setcontext(self.context)
        return new

    def locate(self, start=None, end=None):
        self.start = start
        self.end = end
        return self

    def setcontext(self, context=None):
        self.context = context
        return self

    def modulo(self, factor):
        if self.check(factor):
            return Digit(self.value % factor.value).setcontext(), None

    def power(self, factor):
        if self.check(factor):
            return Digit(pow(self.value, factor.value)).setcontext(), None
        
    def add(self, factor):
        if self.check(factor): 
            return Digit(self.value + factor.value).setcontext(), None

    def minus(self, factor):
        if self.check(factor): 
            return Digit(self.value - factor.value).setcontext(), None

    def multiply(self, factor):
        if self.check(factor): 
            return Digit(self.value * factor.value).setcontext(), None
    
    def divide(self, factor):
        if self.check(factor):
            if factor.value == 0:
                if type(factor) == Digit:
                    return None, DivisionByZeroException(factor.start, factor.end, "Cannot divide by zero", self.context)
                return None, DivisionByZeroException(self.start, self.end, "Cannot divide by zero", self.context)
            return Digit(self.value / factor.value).setcontext(), None
    
    def __repr__(self) -> str:
        return f"{self.value}"

    def check(self, obj):
        return isinstance(obj, Digit)
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
    def equal(self, type, value):
        return self.type == type and self.value == value
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
            if self.current in " \t\r\n":
                self.step()
            elif self.current in DIGITS:
                tokens.append(self.numbers())
            elif self.current in VAR_PTN :
                tokens.append(self.id())
                    
            elif self.current == "%":
                tokens.append(Token(MOD, start=self.position))
                self.step()
            elif self.current == "^":
                tokens.append(Token(POWER, start=self.position))
                self.step()
            elif self.current == "+":
                tokens.append(Token(PLUS, start=self.position))
                self.step()
            elif self.current == "-":
                tokens.append(Token(MINUS, start=self.position))
                self.step()
            elif self.current == "*":
                tokens.append(Token(MUL, start=self.position))
                self.step()
            elif self.current == "/":
                tokens.append(Token(DIV, start=self.position))
                self.step()
            elif self.current == "(":
                tokens.append(Token(LPN, start=self.position))
                self.step()
            elif self.current == ")":
                tokens.append(Token(RPN, start=self.position))
                self.step()
            elif self.current == "!":
                token, error = self.not_equals()
                if error:
                    return [], error
                tokens.append(token)
            elif self.current == "=":
                tokens.append(self.equals())
            elif self.current == "<":
                tokens.append(self.lt())
            elif self.current == ">":
                tokens.append(self.gt())
            else:
                start = self.position.clone()
                char = self.current
                self.step()
                return [], CharacterIllegalException(start, self.position, "Illegal Characteracter '"+char+"'")
        tokens.append(Token(END, start = self.position))

        return tokens,None

    def lt(self):
        ttype = LT
        start = self.position.clone()
        self.step()
        
        if self.current == "=":
            self.step()
            ttype = LTE

        end = self.position
        return Token(type=ttype, start=start, end=end)

    def gt(self):
        ttype = GT
        start = self.position.clone()
        self.step()
        
        if self.current == "=":
            self.step()
            ttype = GTE

        end = self.position
        return Token(type=ttype, start=start, end=end)

    def equals(self):
        ttype = EQ
        start = self.position.clone()
        self.step()
        
        if self.current == "=":
            self.step()
            ttype = EE

        end = self.position
        return Token(type=ttype, start=start, end=end)

    def not_equals(self):
        start = self.position.clone()
        self.step()
        end = self.position
        if self.current == "=":
            self.step()
            end = self.position
            return Token(NE, start=start , end=end), None
        self.step()
        return None, CharacterIllegalException(start, end, "Invalid operater, are you referring '!=' ?")


    def id(self):
        id = ""
        start = self.position.clone()

        while self.current != None and self.current in VAR_PTN + DIGITS + "_":
            id += self.current
            self.step()
        token_type = ID
        for k in KEYWORD_DICT:
            if id == KEYWORD_DICT[k]:
                token_type = KW
        end = self.position
        
        return Token(token_type, id, start, end)
        
    def numbers(self):
        numstr = ""
        dots = 0
        start = self.position.clone()

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
            return Token(INT, int(numstr), start=start, end=self.position )
        else:
            return Token(DEC, float(numstr), start=self.position, end=self.position)

class Number:
    def __init__(self, token) -> None:
        self.token = token

        self.start = token.start
        self.end = token.end
    
    def __repr__(self):
        return f"{self.token}"
class Binary:
    def __init__(self, l, o, r) -> None:
        self.l = l
        self.o = o
        self.r = r

        self.start = l.start
        self.end = r.end

    def __repr__(self) -> str:
        return f"({self.l},{self.o},{self.r})"
class Response:
    def __init__(self) -> None:
        self.node = None
        self.error = None
    def response(self, result):
        if isinstance(result, Response):
            if check(result) :self.error = result.error
            return result.node
        return result
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        self.error = error
        return self
class DataTable:
    def __init__(self) -> None:
        self.data = {}
        self.parent = None

    def get(self, key):
        value = self.data.get(key, None)
        if value == None and self.parent :
            return self.parent.get(key)
        return value

    def set(self, key, value):
        self.data[key] = value

    def pop(self, key):
        del self.data[key]

class RuntimeResponse(Response):
    def __init__(self) -> None:
        self.error = None
        self.value = None

    def response(self, response):

        if check(response):
            self.error = response.error
        return response.value

    def success(self, value):
        self.value = value
        return self
    
class Parser:
    def __init__(self, tokens) -> None:
        self.current = None
        self.tokens = tokens
        self.index = -1
        self.step()
    def parse(self):
        result = self.expr()
        
        if check(result):
            return result.failure(SyntaxIllegalException(self.current.start, self.current.end, "Invalid Syntax"))

        return result
    def step(self):
        self.index += 1
        if self.index < len(self.tokens):
            self.current = self.tokens[self.index]
        return self.current
    def expr(self):
        response = Response()
        if self.current.equal(KW, KEYWORD_DICT["variable_definition"]):
            response.response(self.step())

            if self.current.type != ID:
                response.failure(SyntaxIllegalException(self.current.start, self.current.end, "Expected identifier"))
            
            name = self.current
            response.response(self.step())

            if self.current.type != EQ :
                return response.failure(SyntaxIllegalException(self.current.start, self.current.end, "Expected '='"))

            response.response(self.step())
            expression = response.response(self.expr())
            if response.error :
                return response
            
            return response.success(VariableCreate(name, expression))

        return self.operation(self.term, (PLUS, MINUS))

    def operation(self, get, operation_tokens):
        response = Response()
        l = response.response(get())
        if check(response): return response

        while self.current.type in operation_tokens or (self.current.type,self.current.value) in operation_tokens:
            o = self.current
            response.response(self.step())
            r = response.response(get())
            if check(response): return response
            l = Binary(l, o, r)
        
        return response.success(l)
        
    def term(self):
        return self.operation(self.cell, (MUL, DIV, MOD))

    def cell(self):
        return self.operation(self.element, (POWER,))
    
    def element(self):
        response = Response()
        token = self.current
        if token.type in (PLUS, MINUS):
            response.response(self.step())
            element = response.response(self.element())
            if check(response):
                return response
            return response.success(Unary(token, element))
        elif token.type == ID:
            response.response(self.step())
            return response.success(VariableAccess(token))
        
        elif token.type in (INT, DEC):
            response.response(self.step())
            return response.success(Number(token))
        
        elif token.type == LPN :
            response.response(self.step())
            expression = response.response(self.expr())
            if check(response):
                return response
            if self.current.type == RPN:
                response.response(self.step())
                return response.success(expression)
            else:
                return response.failure(SyntaxIllegalException(self.current.start, self.current.end, "Expected a ')'"))

        return response.failure(SyntaxIllegalException(token.start, token.end, "Expected code "))
class Position:
    def __init__(self, index, line, col, name, text) -> None:
        self.name = name
        self.text = text
        self.index = index
        self.line = line
        self.col = col

    def step(self, current = None):
        self.index += 1
        self.col += 1
        
        if current == "\n":
            self.line += 1
            self.col = 0
        return self
    
    def clone(self):
        return Position(self.index, self.line, self.col, self.name, self.text)
class VariableCreate:
    def __init__(self, name_token, value) -> None:
        self.name_token = name_token
        self.value = value

        self.start = self.name_token.start
        self.end = self.value.end

class VariableAccess:
    def __init__(self, name_token) -> None:
        self.name_token = name_token

        self.start = self.name_token.start
        self.end = self.name_token.end
class Unary:
    def __init__(self, o, n) -> None:
        self.o = o
        self.n = n

        self.start = self.o.start
        self.end = n.end

    def __repr__(self) -> str:
        return f"({self.o},{self.n})"

class Exception:
    def __init__(self, start, end, name, description) -> None:
        self.end = end
        self.start = start
        self.name = name
        self.description = description
    def __repr__(self) -> str:
        result = f"""{self.name}: {self.description}
|-> Code file {self.start.name}, in the line of {self.start.line+1}

    """+arrow(self.start.text, self.start, self.end)

        return result
    def loadcontext(self):
        result = ""
        context = self.context
        position = self.start
        i = 1

        while context:
            i += 1
            result = f"|-> Code file {position.name}, in the line of {str(position.line+1)}, in {context.name}" + result
            position = context.parent_position
            context = context.parent
        return result

        
class RuntimeException(Exception):
    def __init__(self, start, end, name, description, context) -> None:
        super().__init__(start, end, name, description)
        self.context = context

    def __repr__(self) -> str:
        
        result = f"""{self.name}: {self.description}
{self.loadcontext()}
        
    """+arrow(self.start.text, self.start, self.end)
        return result

class DivisionByZeroException(RuntimeException):
    def __init__(self, start, end, description, context) -> None:
        super().__init__(start, end, "DivisionByZeroException", description, context)
        self.context = context

class IllegalException(Exception):
    def __init__(self, start, end, name, description) -> None:
        super().__init__(start, end, name, description)

class TypeInferenceException(Exception):
    def __init__(self, start, end, description) -> None:
        self.start = start
        self.end = end

        super().__init__(start, end, "TypeInferenceException", description)

class SyntaxIllegalException(IllegalException):
    def __init__(self, start, end, description) -> None:
        self.start = start
        self.end = end

        super().__init__(start, end, "SyntaxIllegalException", description)

class CharacterIllegalException(IllegalException):
    def __init__(self, start, end, description) -> None:
        self.start = start
        self.end = end

        super().__init__(start, end, "CharacterIllegalException", description)

class NoValue(Digit):
    def __init__(self) -> None:
        self.value = 0

    def __repr__(self) -> str:
        return "nov"


global_data = DataTable()
global_data.set("nov", NoValue())







