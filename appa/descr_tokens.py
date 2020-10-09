from typing import Tuple

TOK_META = "metarule"
TOK_PP = "percentpercent"
TOK_COLON = "colon"
TOK_IDENT = "ident"
TOK_SEMI = "semicolon"
TOK_OR = "or"
TOK_IGNORE = "ignore"
TOK_EOF = "eof"
TOK_NEWLINE = "newline"

tokens = {
    TOK_META:           r"%\w+",
    TOK_PP:             r"%%",
    TOK_SEMI:           r";",
    TOK_OR:             r"\|",
    TOK_COLON:          r":",
    TOK_IDENT:          r"[a-zA-Z]\w*",
    TOK_IGNORE:         r"[ \t]",
    TOK_NEWLINE:        r"\n",
}

class Token:
    ty: str
    val: str
    range: Tuple[int, int]

    def __init__(self, ty: str, val: str, range: Tuple[int, int]):
        self.ty = ty
        self.val = val
        self.range = range
    def __str__(self):
        return f"({self.ty}) `{self.val}` @[{self.range[0]}..{self.range[1]}]"
    __repr__ = __str__

EOF = Token(TOK_EOF, "⊢", (-1, -1))
