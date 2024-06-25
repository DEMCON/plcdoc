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
        # tokens = iter()
        # tokens = map(token_filter2, tokens)
        # tokens = map(, tokens)
        for token in token_filter(token_filter2(tokenize(source))):
            type = token.kind
            yield lark.lexer.Token(type, token, line=token.row, column=token.column)


@dataclass
class Token:
    kind: str
    text: str
    row: int
    column: int
    comment1: str
    comment2: str


def tokenize(source: str):
    # Note that order is important below:
    token_spec = [
        ("COMMENT1", r"\(\*.*?\*\)"),
        ("COMMENT2", r"//.*?\n"),
        ("OP2", r"(:=)|(==)|(<=)|(!=)|(>=)|(\.\.)"),
        ("OP", r"[<>=:;,\.\(\)\+\-\*\/\[\]]"),
        ("BIN_NUMBER", r"2#[0-1][0-1_]*"),
        ("OCT_NUMBER", r"8#[0-7][0-7_]*"),
        ("DEC_NUMBER", r"10#[0-9][0-9_]*"),
        ("HEX_NUMBER", r"16#[0-9a-fA-F][0-9a-fA-F_]*"),
        ("TIME", r"T#[0-9hHmMsS]+"),
        ("ADDR", r"%[A-Za-z][A-Za-z0-9]*\*"),
        ("REAL1", r"[0-9][0-9_]*[eE][-+]?[0-9]+"),  # example: 1E2
        ("REAL2", r"[0-9][0-9_]*\.[0-9][0-9_]*"),  # example: 1.0
        ("REAL3", r"[0-9][0-9_]*\.[0-9][0-9_]*[eE][-+]?[0-9]+"),  # example: 1.0E2
        ("REAL4", r"\.[0-9][0-9_]*"),  # example: .1
        ("REAL5", r"\.[0-9][0-9_]*[eE][-+]?[0-9]+"),  # example: .1E3
        ("NUMBER", r"[0-9][0-9_]*"),
        ("ID", r"[A-Za-z_][A-Za-z_0-9]*"),
        ("STRING", r"'[^']*'"),
        ("SPACE", r"[ \t]+"),
        ("ATTRIBUTE", r"\{.*?\}"),
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
            elif value in VAR_KEYWORDS:
                kind = "KW_VAR"
            elif value in ACCESS_KEYWORDS:
                kind = "KW_ACCESS"
            elif value in INTEGER_DATA_TYPES:
                kind = "INTTYPE"
        elif kind == "NEWLINE" or kind == "COMMENT2":
            row += 1
            column = 1
        elif kind == "SPACE":
            continue
        elif kind.startswith("REAL"):
            kind = "REAL"
        elif kind.endswith("_NUMBER"):
            kind = "NUMBER"
        elif kind == "OTHER":
            if value.isprintable():
                c = value
            else:
                c = str(value.encode(encoding="utf-8", errors="replace"))
            raise ValueError(f"Unexpected character: {c} at ({row=},{column=})")

        yield Token(kind, value, row, column, "", "")

    yield Token("EOF", "EOF", row, column, "", "")


KEYWORDS = {
    "ABSTRACT",
    "ARRAY",
    "AT",
    "CONSTANT",
    "END_STRUCT",
    "END_TYPE",
    "END_UNION",
    "END_VAR",
    "EXTENDS",
    "FINAL",
    "FUNCTION",
    "FUNCTION_BLOCK",
    "IMPLEMENTS",
    "INTERFACE",
    "METHOD",
    "OF",
    "PERSISTENT",
    "POINTER",
    "PROGRAM",
    "PROPERTY",
    "REFERENCE",
    "STRING",
    "STRUCT",
    "TO",
    "TYPE",
    "UNION",
    "WSTRING",
}

ACCESS_KEYWORDS = {
    "PRIVATE",
    "PROTECTED",
    "PUBLIC",
    "INTERNAL",
}

VAR_KEYWORDS = {
    "VAR",
    "VAR_GLOBAL",
    "VAR_IN_OUT",
    "VAR_INPUT",
    "VAR_INST",
    "VAR_OUTPUT",
    "VAR_STAT",
    "VAR_TEMP",
}

INTEGER_DATA_TYPES = {
    "BYTE",
    "WORD",
    "DWORD",
    "LWORD",
    "SINT",
    "USINT",
    "INT",
    "UINT",
    "DINT",
    "UDINT",
    "LINT",
    "ULINT",
}


def token_filter(tokens):
    """Remove comment tokens, and add comment as attribute to the next token."""
    comment1 = ""
    for token in tokens:
        if token.kind == "SPACE" or token.kind == "NEWLINE":
            continue
        elif token.kind == "COMMENT1":
            comment1 = token.text
            continue
        elif token.kind == "COMMENT2":
            continue
        elif token.kind == "ATTRIBUTE":
            pass
        else:
            if comment1:
                token.comment1 = comment1
            yield token
            comment1 = ""


def token_filter2(tokens):
    previous_token = None
    for token in tokens:
        if token.kind == "COMMENT2":
            if previous_token:
                comment = token.text[2:].strip()
                previous_token.comment1 = comment

        if previous_token:
            yield previous_token
        previous_token = token

    if previous_token:
        yield previous_token
