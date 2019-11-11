import sys
import traceback
from enum import Enum
from typing import List, Optional


def die():
    sys.exit(1)


class TokenType(Enum):
    LITERAL = "[Literal]"
    LP = "("
    RP = ")"
    NOT = "!"
    OR = "v"
    AND = "^"
    EOF = "EOF"


class Token:
    def __init__(self, token_type: TokenType, literal: Optional[str], position: int):
        self.type = token_type
        self.literal = literal
        self.position = position


class Scanner:
    def scan(self, source: str) -> List[Token]:
        self.__reset()
        self.source = source

        while not self.__is_at_end():
            self.start = self.current
            self.__scan_token()

        self.tokens.append(Token(TokenType.EOF, None, self.start))

        return self.tokens

    def __reset(self):
        self.source = ""
        self.tokens: List[Token] = []

        self.start = 0
        self.current = 0

    def __is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def __scan_token(self):
        c = self.__advance()
        if c == " " or c == "\t" or c == "\n":
            return
        elif c == "(":
            self.__add_token(TokenType.LP)
        elif c == ")":
            self.__add_token(TokenType.RP)
        elif c == "!":
            self.__add_token(TokenType.NOT)
        elif c == "v":
            self.__add_token(TokenType.OR)
        elif c == "^":
            self.__add_token(TokenType.AND)
        else:
            if self.__is_alpha(c):
                self.__literal()
            else:
                self.__error(c)

    def __advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def __add_token(self, token_type: TokenType):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, self.start))

    def __is_alpha(self, c: str) -> bool:
        return c is not None and ('a' <= c <= 'z' or 'A' <= c <= 'Z' or c == '_')

    def __is_digit(self, c: str) -> bool:
        return c is not None and ('0' <= c <= '9')

    def __is_alpha_numeric(self, c: Optional[str]) -> bool:
        return self.__is_alpha(c) or self.__is_digit(c)

    def __literal(self):
        while self.__is_alpha_numeric(self.__peek()):
            self.__advance()
        self.__add_token(TokenType.LITERAL)

    def __peek(self) -> Optional[str]:
        if self.__is_at_end():
            return None
        return self.source[self.current]

    def __error(self, c: str):
        msg = f"Unrecognized character `{c}' at position {self.start + 1}\n\n"
        msg += self.source + '\n'
        msg += ' ' * self.start
        msg += '^\n\n'
        # Debug
        msg += f"Debug info\n"
        msg += "=" * 40 + '\n\n'
        msg += "Tokens until now: \n"
        for i, t in enumerate(self.tokens, start=1):
            msg += f"{i} — {t.type} => {t.literal}\n"
        print(msg)
        traceback.print_stack()
        die()


class Expr:
    def __init__(self, expr, negated=False):
        self.expr = expr
        self.negated = negated


class Operation:
    def __init__(self, term1, term2, op, negated=False):
        self.lhs = term1
        self.rhs = term2
        self.op = op
        self.negated = negated


class Literal:
    def __init__(self, literal, negated=False):
        self.literal = literal
        self.negated = negated


class Parser:
    def parse(self, source: str):
        self.source = source
        self.tokens = Scanner().scan(source)
        self.current = 0

        try:
            return self.__expr()
        except:
            raise print("Problem with parsing")

    def __expr(self):
        term1 = self.__term()
        biterm = None

        if self.__match(TokenType.OR):
            term2 = self.__factor()
            biterm = Operation(term1, term2, TokenType.AND)

        while self.__match(TokenType.OR):
            term2 = self.__term()
            biterm = Operation(biterm, term2, TokenType.OR)

        return biterm if biterm else term1


    def __term(self):
        factor1 = self.__factor()
        bifactor = None

        if self.__match(TokenType.AND):
            factor2 = self.__factor()
            bifactor = Operation(factor1, factor2, TokenType.AND)

        while self.__match(TokenType.AND):
            factor2 = self.__factor()
            bifactor = Operation(bifactor, factor2, TokenType.AND)

        return bifactor if bifactor else factor1


    def __factor(self):
        negated = False
        if self.__match(TokenType.NOT):
            negated = True

        if self.__match(TokenType.LP):
            expr = self.__expr()
            self.__consume(TokenType.RP)
            return Expr(expr, negated)
        else:
            tok = self.__consume(TokenType.LITERAL)
            literal = tok.literal
            return Literal(literal, negated)

    def __match(self, token_type):
        if self.__check(token_type):
            self.__advance()
            return True
        return False

    def __consume(self, token_type):
        if self.__check(token_type):
            return self.__advance()
        raise (self.__actual(), "Parsing problem")

    def __check(self, token_type):
        if self.__is_at_end():
            return False
        return self.__actual().type == token_type

    def __advance(self):
        if not self.__is_at_end():
            self.current += 1
            return self.__previous()

    def __is_at_end(self):
        return self.__actual().type == TokenType.EOF

    def __actual(self):
        return self.tokens[self.current]

    def __previous(self):
        return self.tokens[self.current - 1]


def print_literal(literal, clause):
    if literal.negated:
        clause += "!"
    clause += literal.literal
    return clause


def print_op(operation, clause):
    if operation.negated:
        clause += "!"

    clause += stringify(operation.lhs)

    clause += f" {operation.op.value} "

    clause += stringify(operation.rhs)
    return clause


def print_expr(expr, clause):
    if expr.negated:
        clause += "!"
    clause += "("
    clause += stringify(expr.expr)
    clause += ")"
    return clause


def stringify(ast, clause=""):
    if isinstance(ast, Literal):
        return print_literal(ast, clause)
    elif isinstance(ast, Operation):
        return print_op(ast, clause)
    elif isinstance(ast, Expr):
        return print_expr(ast, clause)
