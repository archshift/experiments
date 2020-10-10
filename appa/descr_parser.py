import re

from descr_ast import *
from descr_tokens import *

def make_token_regex(token_descs):
    def single_regex(desc):
        if "tok" in desc:
            return f"?P<{desc['tok']}>{desc['regexp']}"
        else:
            return desc['regexp']

    regexps = map(single_regex, token_descs)
    return '(' + ')|('.join(regexps) + ')'

token_state_matchers = {
    state: re.compile(make_token_regex(descs))
    for state, descs in token_states.items()
}

def match_transitions(token_descs):
    return { desc["tok"]: desc["next"] for desc in token_descs if "next" in desc }

state_transitions = {
    state: match_transitions(descs)
    for state, descs in token_states.items()
}

def tokenize(file):
    state = init_state
    matcher = token_state_matchers[state]

    for li, line in enumerate(file):
        offs = 0
        while match := matcher.match(line):
            groups = match.groupdict()
            try:
                ty, val = next((k, groups[k]) for k in groups if groups[k] is not None)
                span_a, span_b = match.span(ty)
                yield Token(ty, val, Pos(li+1, span_a + offs, li+1, span_b + offs))
            except StopIteration:
                # no emitted token
                pass

            line = line[match.end():]
            offs += match.end()

            if ty in state_transitions[state]:
                # change of state required
                state = state_transitions[state][ty]
                matcher = token_state_matchers[state]

def parse_meta(peek, seek) -> Meta:
    operator = seek(TOK_META)
    operands = []
    while peek() != TOK_NEWLINE:
        operands.append(seek(TOK_IDENT))

    seek(TOK_NEWLINE)
    return (AST_META, operator, operands)

def parse_rule(peek, seek) -> Rule:
    name = seek(TOK_IDENT)
    seek(TOK_COLON)

    productions: List[Production] = []
    prod_idents: List[Token] = []
    
    while peek() not in [TOK_SEMI, TOK_EOF]:
        if peek() == TOK_OR:
            or_tok = seek(TOK_OR)
            prod = Production(prod_idents)
            if not prod.pos:
                prod.pos = or_tok.pos
            productions.append(prod)
            prod_idents = []
        else:
            prod_idents.append(seek(TOK_IDENT))
    
    semi_tok = seek(TOK_SEMI)
    prod = Production(prod_idents)
    productions.append(prod)
    if not prod.pos:
        prod.pos = semi_tok.pos

    return Rule(name, productions)

def parse_rules(peek, seek) -> List[Rule]:
    rules = []

    while peek() != TOK_EOF:
        rules.append(parse_rule(peek, seek))

    return rules

def parse_descr(peek, seek):
    metas = []
    while peek() != TOK_PP:
        if peek() == TOK_NEWLINE:
            seek(TOK_NEWLINE)
        metas.append(parse_meta(peek, seek))

    seek(TOK_PP)

    rules = parse_rules(peek, seek)
    
    return (AST_DESCR, metas, rules)

def parse(file):
    token_gen = tokenize(file)
    lookahead = []
    def fill_lookahead():
        while len(lookahead) < 2:
            try:
                lookahead.append(next(token_gen))
            except StopIteration:
                lookahead.append(EOF)
    def peek(i=0):
        fill_lookahead()
        return lookahead[i].ty
    def seek(token):
        if (ty := peek()) != token:
            raise RuntimeError(f"Parse error. Expected token of type `{token}`, but got `{peek()}`!")
        out = lookahead[0]
        del lookahead[0]
        return out
    return parse_descr(peek, seek)

