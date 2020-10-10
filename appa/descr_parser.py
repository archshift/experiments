from descr_ast import *
from descr_tokens import *
from descr_lexer import *

from typing import Dict, Any

def parse_meta(peek, seek) -> Meta:
    operator = seek(TOK_META)
    operands = []
    while peek() != TOK_NEWLINE:
        operands.append(seek(TOK_IDENT))

    seek(TOK_NEWLINE)
    return (AST_META, operator, operands)

def parse_production(peek, seek) -> Production:
    idents: List[Token] = []
    rule_code: Optional[Token] = None
    while peek() == TOK_IDENT:
        idents.append(seek(TOK_IDENT))
    
    if peek() == TOK_RULE_CODE:
        rule_code = seek(TOK_RULE_CODE)
    return Production(idents, rule_code)

def parse_rule(peek, seek) -> Rule:
    name = seek(TOK_IDENT)
    seek(TOK_COLON)

    productions: List[Production] = []
    term: Token = None

    while True:
        prod = parse_production(peek, seek)
        if peek() == TOK_SEMI:
            term = seek(TOK_SEMI)
        else:
            term = seek(TOK_OR)

        if not prod.pos:
            prod.pos = term.pos
        productions.append(prod)

        if term.ty == TOK_SEMI:
            break

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
            raise RuntimeError(f"Parse error. Expected token of type `{token}`, but got `{ty}`!")
        out = lookahead[0]
        del lookahead[0]
        return out
    return parse_descr(peek, seek)

