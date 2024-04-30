"""
PLC lexer.

"""

import re

from dataclasses import dataclass
import lark.lexer


class MyLexer(lark.lexer.Lexer):
    def __init__(self, lexer_conf):
        pass

    def lex(self, source):
        # print(code)
        for token in token_filter(tokenize(source)):
            type = token.kind
            yield lark.lexer.Token(type, token)


@dataclass
class Token:
    kind: str
    text: str
    row: int
    column: int
    comment1: str


def tokenize(source: str):
    # Note that order is important below:
    token_spec = [
        ("COMMENT1", r"\(\*.*?\*\)"),
        ("COMMENT2", r"//.*?\n"),
        ("OP2", r"(:=)|(==)|(<=)|(!=)|(>=)|(\.\.)"),
        ("OP", r"[<>=:;,\.\(\)\+\-\*\/]"),
        ("BIN_NUMBER", r"2#[0-1][0-1_]*"),
        ("OCT_NUMBER", r"8#[0-7]+"),
        ("HEX_NUMBER", r"16#[0-9a-fA-F][0-9a-fA-F_]*"),
        ("TIME", r"T#[0-9a-fA-F][0-9a-fA-F_]*"),
        ("REAL", r"[0-9]+\.[0-9]+"),
        ("NUMBER", r"[0-9]+"),
        ("ID", r"[A-Za-z][A-Za-z_0-9]*"),
        ("STRING", r"'[^']*'"),
        ("SPACE", r"[ \t]+"),
        ("ATTRIBUTE", r"\{attribute.*?\}"),
        ("NEWLINE", r"\n"),
        ("OTHER", r"."),
    ]
    op_names = {
        ":=": "COLON_EQUALS",
        ":": "COLON",
        ";": "SEMI",
        ",": "COMMA",
        ".": "DOT",
        "..": "DOTDOT",
        "+": "PLUS",
        "-": "MINUS",
        "*": "ASTERIX",
        "/": "SLASH",
        "{": "BRACE_OPEN",
        "}": "BRACE_CLOSE",
        "(": "PARENTHESIS_OPEN",
        ")": "PARENTHESIS_CLOSE",
        "[": "BRACKET_OPEN",
        "]": "BRACKET_CLOSE",
    }

    regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_spec)
    row = 1
    column = 1

    for mo in re.finditer(regex, source, re.MULTILINE | re.DOTALL):
        kind: str = mo.lastgroup
        value = mo.group()
        if kind == "OP" or kind == "OP2":
            kind = op_names[value]
        elif kind == "ID":
            if value in KEYWORDS:
                kind = "KW_" + value
        elif kind == "NEWLINE":
            row += 1
        elif kind == "OTHER":
            if value.isprintable():
                c = value
            else:
                c = str(value.encode(encoding="utf-8", errors="replace"))
            raise ValueError(f"Unexpected character: {c}")

        yield Token(kind, value, row, column, "")

    yield Token("EOF", "EOF", row, column, "")


KEYWORDS = {
    "ABSTRACT",
    "ARRAY",
    "END_STRUCT",
    "END_TYPE",
    "END_VAR",
    "EXTENDS",
    "FINAL",
    "FUNCTION",
    "FUNCTION_BLOCK",
    "INTERFACE",
    "INTERNAL",
    "METHOD",
    "OF",
    "POINTER",
    "PROGRAM",
    "PROPERTY",
    "PRIVATE",
    "PROTECTED",
    "PUBLIC",
    "REFERENCE",
    "STRING",
    "STRUCT",
    "TO",
    "TYPE",
    "VAR",
    "VAR_GLOBAL",
    "VAR_INPUT",
    "VAR_OUTPUT",
}


def token_filter(tokens):
    comment1 = ""
    attr = ""
    for token in tokens:
        if token.kind == "SPACE" or token.kind == "NEWLINE":
            continue
        elif token.kind == "COMMENT1":
            comment1 = token.text
            continue
        elif token.kind == "COMMENT2":
            continue
        elif token.kind == "ATTRIBUTE":
            attr = token.text
        else:
            token.comment1 = comment1
            yield token
            comment1 = ""
