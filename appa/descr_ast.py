from typing import List, Tuple
from descr_tokens import Token

AST_META = "meta"
AST_DESCR = "descr"
AST_PRODUCTION = "production"
AST_RULE = "rule"

Type = str
Meta = Tuple[Type, Token, List[Token]]
Production = Tuple[Type, List[Token]]
Rule = Tuple[Type, Token, List[Production]]
Ast = Tuple[Type, List[Meta], List[Rule]]

def ast_rules(ast: Ast) -> List[Rule]:
    return ast[2]

def rule_name(rule: Rule) -> str:
    return rule[1].val

def rule_productions(rule: Rule) -> List[Production]:
    return rule[2]

def rule_production(rule: Rule, i: int) -> Production:
    return rule_productions(rule)[i]

def production_idents(prod: Production) -> List[Token]:
    return prod[1]