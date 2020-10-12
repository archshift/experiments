from typing import List, Tuple, Optional, Union, Dict
from descr_tokens import Token, Pos

AST_META = "meta"
AST_DESCR = "descr"
AST_PRODUCTION = "production"
AST_RULE = "rule"

Type = str

class MetaToken:
    tys: List[Optional[Token]]
    names: List[Token]
    def __init__(self, tys: List[Optional[Token]], names: List[Token]):
        self.tys = tys
        self.names = names
    def __str__(self):
        token_decls = ( f'{name.val}: {ty.val if ty else None}'
                        for name, ty in zip(self.names, self.tys) )
        return f'(%token {", ".join(token_decls)})'
    __repr__ = __str__

class MetaStart:
    rule: Token
    def __init__(self, rule: Token):
        self.rule = rule
    def __str__(self):
        return f'(%start {self.rule.val})'
    __repr__ = __str__

class MetaUnion:
    types_vars: List[Tuple[Token, Token]]
    def __init__(self, typed_vars: List[Tuple[Token, Token]]):
        self.types_vars = typed_vars
    def __str__(self):
        var_decls = ( f'({name.val}: {ty.val})'
                        for ty, name in self.types_vars )
        return f'(%union {" ".join(var_decls)})'
    __repr__ = __str__
        

Meta = Union[MetaToken, MetaStart, MetaUnion]

class Production:
    toks: List[Token]
    action: Optional[Token]
    pos: Pos
    def __init__(self, toks: List[Token], action: Optional[Token], start_pos: Pos):
        self.toks = toks
        self.action = action
        self.pos = start_pos
        if toks:
            self.pos = Pos.bounds(tok.pos for tok in toks)
        if action:
            self.pos = Pos.bounds(self.pos, action.pos)
    def __str__(self):
        return ' '.join( p.val for p in self.toks )
    __repr__ = __str__

class Rule:
    name: Token
    prods: List[Production]
    pos: Pos
    def __init__(self, name: Token, prods: List[Production]):
        self.name = name
        self.prods = prods
        self.pos = Pos.bounds(name.pos, (prod.pos for prod in prods))
    def __str__(self):
        left = f'{self.name.val} ::= '
        left_size = len(left)
        padding = ' ' * (left_size - 2)
        str_prods = map(str, self.prods)
        return left + f'\n{padding}| '.join(str_prods) + f';  @{self.pos}'
    __repr__ = __str__

Ast = Tuple[Type, List[Meta], List[Rule]]

def ast_rules(ast: Ast) -> List[Rule]:
    return ast[2]
