from descr_ast import *
from descr_tokens import *
from descr_lexer import *

from typing import Dict, Any

def parse_meta_token(peek, seek) -> MetaToken:
    tys: List[Optional[Token]] = []
    names: List[Token] = []
    last_ty: Optional[Token] = None

    while peek() != TOK_NEWLINE:
        if peek() == TOK_LANGLE:
            seek(TOK_LANGLE)
            last_ty = seek(TOK_IDENT)
            seek(TOK_RANGLE)
        tys.append(last_ty)
        names.append(seek(TOK_IDENT))

    seek(TOK_NEWLINE)
    return MetaToken(tys, names)

def parse_meta_start(peek, seek) -> MetaStart:
    rule = seek(TOK_IDENT)
    seek(TOK_NEWLINE)
    return MetaStart(rule)

def parse_meta_union(peek, seek) -> MetaUnion:
    decls: List[Tuple[Token, Token]] = []
    seek(TOK_LBRACKET)
    seek(TOK_NEWLINE)
    while peek() != TOK_RBRACKET:
        decls.append((seek(TOK_IDENT), seek(TOK_IDENT)))
        seek(TOK_SEMI)
        seek(TOK_NEWLINE)
    seek(TOK_RBRACKET)
    seek(TOK_NEWLINE)
    return MetaUnion(decls)

def parse_meta(peek, seek) -> Meta:
    meta = seek(TOK_META)
    if meta.val in { '%token', '%type', '%left', '%right', '%nonassoc', '%precedence' }:
        return parse_meta_token(peek, seek)
    elif meta.val == '%start':
        return parse_meta_start(peek, seek)
    elif meta.val == '%union':
        return parse_meta_union(peek, seek)
    else:
        raise RuntimeError(f"Unknown meta token `{meta}`!")

def parse_production(peek, seek, start_pos: Pos) -> Production:
    idents: List[Token] = []
    rule_code: Optional[Token] = None
    while peek() == TOK_IDENT:
        idents.append(seek(TOK_IDENT))
    
    if peek() == TOK_RULE_CODE:
        rule_code = seek(TOK_RULE_CODE)
    return Production(idents, rule_code, start_pos)

def parse_rule(peek, seek) -> Rule:
    name = seek(TOK_IDENT)
    term = seek(TOK_COLON)

    productions: List[Production] = []

    while True:
        start_pos = Pos(term.pos.l1, term.pos.c1 + 1, term.pos.l1, term.pos.c1 + 1)
        prod = parse_production(peek, seek, start_pos)

        productions.append(prod)

        if peek() == TOK_OR:
            term = seek(TOK_OR)
        else:
            break

    seek(TOK_SEMI)
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
        else:
            metas.append(parse_meta(peek, seek))

    seek(TOK_PP)

    rules = parse_rules(peek, seek)
    
    return (AST_DESCR, metas, rules)

def parse(file, debug_lexer=False):
    token_gen = tokenize(file, debug_lexer=debug_lexer)
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

