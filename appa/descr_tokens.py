from typing import Tuple, Union, Iterator
import tools

TOK_META = "metarule"
TOK_PP = "percentpercent"
TOK_COLON = "colon"
TOK_IDENT = "ident"
TOK_SEMI = "semicolon"
TOK_OR = "or"
TOK_EOF = "eof"
TOK_NEWLINE = "newline"

STATE_META = "meta"
STATE_RULES = "rules"
init_state = STATE_META

meta_tokens = [
    {"regexp": r"%\w+",         "tok": TOK_META},
    {"regexp": r"%%\n",         "tok": TOK_PP,      "next": STATE_RULES},
    {"regexp": r"[ \t]"},
]
rules_tokens = [
    {"regexp": r";",            "tok": TOK_SEMI},
    {"regexp": r"\|",           "tok": TOK_OR},
    {"regexp": r":",            "tok": TOK_COLON},
    {"regexp": r"[a-zA-Z]\w*",  "tok": TOK_IDENT},
    {"regexp": r"[ \t\n]"},
]
token_states = {
    STATE_META:  meta_tokens,
    STATE_RULES: rules_tokens,
}


class Pos:
    l1: int
    l2: int
    c1: int
    c2: int
    def __init__(self, l1: int, c1: int, l2: int, c2: int):
        self.l1, self.l2 = l1, l2
        self.c1, self.c2 = c1, c2

    @staticmethod
    def bounds(*args: Union["Pos", Iterator["Pos"]]):
        left, right = tools.minmax(tools.flatten(*args))
        l1, c1 = left.l1, left.c1
        l2, c2 = right.l2, right.c2
        return Pos(l1, c1, l2, c2)

    def __lt__(self, other: "Pos"):
        return self.l1 < other.l1 or (self.l1 == other.l1 and self.c1 < other.c1)
    def __le__(self, other: "Pos"):
        return (self.l1, self.c1) == (other.l1, other.c1) or self < other
    def __gt__(self, other: "Pos"):
        return self.l2 > other.l2 or (self.l2 == other.l2 and self.c2 > other.c2)
    def __ge__(self, other: "Pos"):
        return (self.l2, self.c2) == (other.l2, other.c2) or self > other
    def __str__(self):
        return f"[L{self.l1}:{self.c1}, L{self.l2}:{self.c2}]"
    __repr__ = __str__

class Token:
    ty: str
    val: str
    pos: Pos

    def __init__(self, ty: str, val: str, pos: Pos):
        self.ty = ty
        self.val = val
        self.pos = pos
    def __str__(self):
        return f"({self.ty}) `{self.val}` @{self.pos}"
    __repr__ = __str__

EOF = Token(TOK_EOF, "⊢", Pos(-1, -1, -1, -1))
