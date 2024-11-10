import re

class TokenType:
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MUL = 'MUL'
    DIV = 'DIV'
    INT = 'INT'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    EOF = 'EOF'

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS)
            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS)
            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MUL)
            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIV)
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN)
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN)
            if self.current_char.isdigit():
                return Token(TokenType.INT, self.integer())
            raise Exception('Невідомий символ')

        return Token(TokenType.EOF)

class AST:
    pass

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Num(AST):
    def __init__(self, value):
        self.value = value

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Paren(AST):
    def __init__(self, expr):
        self.expr = expr

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f'Помилка синтаксису: очікується {token_type}')

    def factor(self):
        token = self.current_token
        if token.type == TokenType.INT:
            self.eat(TokenType.INT)
            return Num(token.value)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return Paren(node)
        elif token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return UnaryOp(token, self.factor())
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOp(token, self.factor())

    def term(self):
        node = self.factor()

        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            if token.type == TokenType.MUL:
                self.eat(TokenType.MUL)
            elif token.type == TokenType.DIV:
                self.eat(TokenType.DIV)
            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def expr(self):
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
            node = BinOp(left=node, op=token, right=self.term())

        return node

class Interpreter:
    def __init__(self, parser):
        self.parser = parser

    def interpret(self):
        return self.visit(self.parser.expr())

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name)
        return method(node)

    def visit_BinOp(self, node):
        if node.op.type == TokenType.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == TokenType.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == TokenType.MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == TokenType.DIV:
            right_value = self.visit(node.right)
            if right_value == 0:
                raise ZeroDivisionError("Ділення на нуль!")
            return self.visit(node.left) / right_value

    def visit_Num(self, node):
        return node.value

    def visit_UnaryOp(self, node):
        if node.op.type == TokenType.PLUS:
            return +self.visit(node.expr)
        elif node.op.type == TokenType.MINUS:
            return -self.visit(node.expr)

    def visit_Paren(self, node):
        return self.visit(node.expr)

# Тестові випадки
test_cases = [
    "(2 + 3) * 4",            # 20
    "10 + 2 * 5",             # 20
    "3 + 5 * (2 + 2)",        # 23
    "7 * (3 + 2) - 5",        # 30
    "(3 + 2) * (5 - 3) / 2"   # 5
]

lexer = Lexer
parser = Parser
interpreter = Interpreter

for text in test_cases:
    lexer_instance = lexer(text)
    parser_instance = parser(lexer_instance)
    interpreter_instance = interpreter(parser_instance)
    result = interpreter_instance.interpret()
    print(f"Вираз: {text} = {result}")