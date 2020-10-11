from typing import Callable, Optional, List, Dict, Any, Iterator
import re

def lex_print(*args):
    print("[LEX]: ", *args)

from descr_tokens import *

TOK_META = "metarule"
TOK_PP = "percentpercent"
TOK_COLON = "colon"
TOK_IDENT = "ident"
TOK_SEMI = "semicolon"
TOK_OR = "or"
TOK_LBRACKET = "lbracket"
TOK_LANGLE = "langle"
TOK_RANGLE = "rangle"
TOK_RULE_CODE = "rule_code"
TOK_ANY = "any"
TOK_EOF = "eof"
TOK_NEWLINE = "newline"
TOK_ST_COMMENT = "st_comment"
TOK_END_COMMENT = "end_comment"
TOK_COMMENT = "comment"
TOK_WHITESPACE = "whitespace"

STATE_META = "meta"
STATE_RULES = "rules"
STATE_RULE_CODE = "rule_code"
STATE_COMMENT = "comment"
init_state = STATE_META

class TokenCtx:
    goto: Callable[[str], None]
    state: Callable[[], str]
    match: "Token"
    prev_state: Optional[str] = None
    def push_state(self, state):
        assert self.prev_state is None
        self.prev_state = self.state()
        self.goto(state)
    def pop_state(self):
        assert self.prev_state is not None
        self.goto(self.prev_state)
        self.prev_state = None

    bracket_stack: int = 0
    rule_code: Optional["Token"] = None
    def push_bracket_stack(self): self.bracket_stack += 1
    def pop_bracket_stack(self) -> int:
        self.bracket_stack -= 1
        return self.bracket_stack
    def push_rule_code(self, tok: "Token"):
        if self.rule_code is None:
            self.rule_code = tok
            self.rule_code.ty = TOK_RULE_CODE
            return
        self.rule_code.val += tok.val
        self.rule_code.pos = Pos.bounds(self.rule_code.pos, tok.pos)
    def pop_rule_code(self) -> "Token":
        out = self.rule_code
        self.rule_code = None
        assert out is not None
        return out

TokenState = List[Dict[str, Any]]
TokenStates = Dict[str, TokenState]
TokenAction = Callable[[TokenCtx], Optional["Token"]]

meta_tokens: TokenState = [
    { "regexp": r"%\w+",        "tok": TOK_META },
    { "regexp": r"[a-zA-Z]\w*", "tok": TOK_IDENT },
    { "regexp": r"\n",          "tok": TOK_NEWLINE},
    { "regexp": r"<",           "tok": TOK_LANGLE },
    { "regexp": r">",           "tok": TOK_RANGLE },
    { "regexp": r"%%\n",        "tok": TOK_PP,          "do": lambda ctx: ctx.goto(STATE_RULES) or ctx.match },
    { "regexp": r"/\*",         "tok": TOK_ST_COMMENT,  "do": lambda ctx: ctx.push_state(STATE_COMMENT) },
    { "regexp": r"[ \t]+",      "tok": TOK_WHITESPACE,  "do": lambda _: None },
    { "regexp": r"//[^\n]*",    "tok": TOK_COMMENT,     "do": lambda _: None },
]
rules_tokens: TokenState = [
    { "regexp": r";",           "tok": TOK_SEMI },
    { "regexp": r"\|",          "tok": TOK_OR },
    { "regexp": r":",           "tok": TOK_COLON },
    { "regexp": r"[a-zA-Z]\w*", "tok": TOK_IDENT },
    { "regexp": r'\{',          "tok": TOK_LBRACKET,    "do": lambda ctx: ctx.goto(STATE_RULE_CODE)
                                                                       or ctx.push_bracket_stack() },
    { "regexp": r"/\*",         "tok": TOK_ST_COMMENT,  "do": lambda ctx: ctx.push_state(STATE_COMMENT) },
    { "regexp": r"[ \t\n]+",    "tok": TOK_WHITESPACE,  "do": lambda _: None },
    { "regexp": r"//[^\n]*",    "tok": TOK_COMMENT,     "do": lambda _: None },
]
rule_code_tokens: TokenState = [
    { "regexp": r'\{',          "tok": TOK_LBRACKET,    "do": lambda ctx: ctx.push_bracket_stack() \
                                                                       or ctx.push_rule_code(ctx.match) \
                                                                       or ctx.match },
    { "regexp": r'\}',          "tok": TOK_RULE_CODE,   "do": lambda ctx: (ctx.goto(STATE_RULES) or ctx.pop_rule_code())
                                                                        if not ctx.pop_bracket_stack()
                                                                        else ctx.push_rule_code(ctx.match) },
    { "regexp": r'(.|\n)',      "tok": TOK_ANY,         "do": lambda ctx: ctx.push_rule_code(ctx.match) }
]
comment_tokens: TokenState = [
    { "regexp": r"\*/",         "tok": TOK_END_COMMENT, "do": lambda ctx: ctx.pop_state() },
    { "regexp": r'([^*]|\*[^/])+', "tok": TOK_COMMENT,  "do": lambda _: None },
]
token_states: TokenStates = {
    STATE_META:         meta_tokens,
    STATE_RULES:        rules_tokens,
    STATE_RULE_CODE:    rule_code_tokens,
    STATE_COMMENT:      comment_tokens,
}

EOF = Token(TOK_EOF, "⊢", Pos(-1, -1, -1, -1))



def make_token_regex(token_descs):
    def single_regex(desc):
        if desc["tok"] is not None:
            return f"?P<{desc['tok']}>{desc['regexp']}"
        else:
            return desc['regexp']

    regexps = map(single_regex, token_descs)
    return '(' + ')|('.join(regexps) + ')'

def make_token_actions(token_descs):
    def single_action(desc):
        if "do" in desc:
            return desc["do"]
        else:
            return lambda ctx: ctx.match

    return { desc["tok"]: single_action(desc) for desc in token_descs }

token_state_matchers: Dict[str, Any] = {
    state: re.compile(make_token_regex(descs))
    for state, descs in token_states.items()
}

token_actions: Dict[str, Dict[str, TokenAction]] = {
    state: make_token_actions(descs)
    for state, descs in token_states.items()
}

def tokenize(file, debug_lexer=False) -> Iterator[Token]:
    state = init_state
    matcher = token_state_matchers[state]
    tok: Optional[Token]
    if debug_lexer: lex_print(f"Starting state {init_state}")

    def goto(which: str):
        nonlocal state
        nonlocal matcher
        state = which
        matcher = token_state_matchers[state]
        if debug_lexer: lex_print(f"Goto state {which}")

    ctx = TokenCtx()
    ctx.goto = goto
    ctx.state = lambda: state

    for li, line in enumerate(file):
        offs = 0
        while line:
            match = matcher.match(line)
            if not match:
                raise RuntimeError(f"Could not match {repr(line)} at L{li}:{offs}")

            groups = match.groupdict()
            ty, val = next((k, groups[k]) for k in groups if groups[k] is not None)
            span_a, span_b = match.span(ty)
            tok = Token(ty, val, Pos(li+1, span_a + offs, li+1, span_b + offs))
            ctx.match = tok
            tok = token_actions[state][ty](ctx)
            if tok is not None:
                if debug_lexer: lex_print(tok)
                yield tok
            elif debug_lexer:
                lex_print(f"Skipping token `{ty}` = {repr(match.group(0))}")

            line = line[match.end():]
            offs += match.end()
