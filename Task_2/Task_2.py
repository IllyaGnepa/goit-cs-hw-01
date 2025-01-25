import re

class Lexer:
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

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None 
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char in ' \t':
            self.advance()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char in ' \t':
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return self.Token(self.INT, self.integer())

            if self.current_char == '+':
                self.advance()
                return self.Token(self.PLUS)

            if self.current_char == '-':
                self.advance()
                return self.Token(self.MINUS)

            if self.current_char == '*':
                self.advance()
                return self.Token(self.MUL)

            if self.current_char == '/':
                self.advance()
                return self.Token(self.DIV)

            if self.current_char == '(':
                self.advance()
                return self.Token(self.LPAREN)

            if self.current_char == ')':
                self.advance()
                return self.Token(self.RPAREN)

            self.error()

        return self.Token(self.EOF)


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        token = self.current_token
        if token.type == Lexer.INT:
            self.eat(Lexer.INT)
            return token.value
        elif token.type == Lexer.LPAREN:
            self.eat(Lexer.LPAREN)
            result = self.expr()
            self.eat(Lexer.RPAREN)
            return result

    def term(self):
        result = self.factor()
        while self.current_token.type in (Lexer.MUL, Lexer.DIV):
            token = self.current_token
            if token.type == Lexer.MUL:
                self.eat(Lexer.MUL)
                result *= self.factor()
            elif token.type == Lexer.DIV:
                self.eat(Lexer.DIV)
                result /= self.factor()
        return result

    def expr(self):
        result = self.term()
        while self.current_token.type in (Lexer.PLUS, Lexer.MINUS):
            token = self.current_token
            if token.type == Lexer.PLUS:
                self.eat(Lexer.PLUS)
                result += self.term()
            elif token.type == Lexer.MINUS:
                self.eat(Lexer.MINUS)
                result -= self.term()
        return result


class Interpreter:
    def __init__(self, parser):
        self.parser = parser

    def interpret(self):
        return self.parser.expr()


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