from typing import List, Tuple
from descr_tokens import Token, Pos

AST_META = "meta"
AST_DESCR = "descr"
AST_PRODUCTION = "production"
AST_RULE = "rule"

Type = str
Meta = Tuple[Type, Token, List[Token]]

class Production:
    toks: List[Token]
    pos: Pos = None
    def __init__(self, toks: List[Token]):
        self.toks = toks
        if toks:
            self.pos = Pos.bounds(tok.pos for tok in toks)
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
