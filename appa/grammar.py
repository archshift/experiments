from typing import List, Set, Tuple, Dict, FrozenSet, Union

import descr_ast as ast
import descr_tokens as tok
from tools import BijectMap

class EOF:
    def __str__(self): return '⊢'
    __repr__ = __str__
Token = Union[str, EOF]

Lr1Item = Tuple[int, int, int, Token]
Lr1Set = Set[Lr1Item]
Lr1FrSet = FrozenSet[Lr1Item]

def make_token(ident: ast.Token) -> Token:
    if ident is tok.EOF:
        return EOF()
    return ident.val
    

def lr1_items(rules: List[ast.Rule], base_item: Lr1Item, seen=set()) -> Lr1Set:
    """
    Get all the possible parser positions that mirror the given production's
    dot position.
    """
    
    rule_id, prod_id, dot, lookahead = base_item
    rule_map: Dict[Token, int] = { make_token(rule.name): i for i, rule in enumerate(rules) }

    out = { (rule_id, prod_id, dot, lookahead) }
    if out & seen:
        return set()

    prod = rules[rule_id].prods[prod_id]
    tokens = prod.toks
    if dot == len(tokens):
        return out
    if dot > len(tokens):
        return set()

    next_tok = make_token(tokens[dot])
    next_lookahead = make_token(tokens[dot+1]) if dot+1 < len(tokens) else lookahead

    if next_tok in rule_map:
        next_rule_id = rule_map[next_tok]
        next_rule = rules[next_rule_id]
        next_prods = next_rule.prods
        
        for next_prod_id in range(len(next_prods)):
            next_item = (next_rule_id, next_prod_id, 0, next_lookahead)
            out |= lr1_items(rules, next_item, seen | out)
    
    return out

class Reduce(Tuple[int, int]): pass
class Shift(int): pass
Action = Union[Shift, Reduce]

def extend_states(rules: List[ast.Rule], item_set: Lr1FrSet, states: BijectMap[int, Lr1FrSet]) -> Dict[Token, Action]:
    new_states: Dict[Token, Lr1Set] = {}
    actions: Dict[Token, Action] = {}

    for rid, pid, dot, lookahead in item_set:
        rule = rules[rid]
        prod = rule.prods[pid]
        tokens = prod.toks

        if dot == len(tokens):
            # At the end of a rule, so we can reduce now
            new_action = Reduce((rid, pid))
            if lookahead in actions:
                old_action = actions[lookahead]
                print(f"Reduce/Reduce conflict on `{lookahead}` in state {states.get_b(item_set)}! " +
                      f"between action {pretty_action(rules, old_action)} and {pretty_action(rules, new_action)}")
            actions[lookahead] = new_action
            continue

        # If we didn't reduce, we're shifting to the next dot positions in the set
        next_token = make_token(tokens[dot])
        next_item = (rid, pid, dot + 1, lookahead)
        if next_token not in new_states:
            new_states[next_token] = set()

        new_states[next_token] |= lr1_items(rules, next_item, new_states[next_token])

    for tok in new_states:
        # Obtain indices of shift states in the state map
        state = frozenset(new_states[tok])
        if state not in states:
            states.insert_ab(len(states), state)
        state_idx = states.get_b(state)
        
        new_action = Shift(state_idx)
        if tok in actions:
            old_action = actions[tok]
            print(f"Shift/Reduce conflict on `{tok}` in state {states.get_b(item_set)}! " +
                  f"between action {pretty_action(rules, old_action)} and {pretty_action(rules, new_action)}")
        actions[tok] = new_action
    return actions

def make_graph(rules: List[ast.Rule], rule_id: int):
    prods = rules[rule_id].prods

    states: BijectMap[int, Lr1FrSet] = BijectMap()

    # Start by adding the initial state, with all of the start productions.
    start_set = set()
    for prod_id in range(len(prods)):
        start_set |= lr1_items(rules, (rule_id, prod_id, 0, EOF()))
    states.insert_ab(0, frozenset(start_set))

    # Our output actions
    actions: List[Dict[Token, Action]] = [{}]

    # This frontier is used for recursion elimination.
    # Stack with the states yet to be visited.
    frontier = [0]
    while len(frontier):
        curr_state_idx = frontier.pop()
        curr_state = states.get_a(curr_state_idx)

        found_actions = extend_states(rules, curr_state, states)

        while len(actions) < len(states):
            frontier.append(len(actions))
            actions.append({})
        
        for next_tok, action in found_actions.items():
            actions[curr_state_idx][next_tok] = action
    
    return states, actions

def pretty_lr1_item(rules: List[ast.Rule], item: Lr1Item):
    rid, pid, dot, lookahead = item
    rule = rules[rid]
    prod = rule.prods[pid]
    tokens = prod.toks
    str_tokens = ' '.join( str(make_token(p)) for p in tokens[:dot] ) \
         + " 🠷 " + ' '.join( str(make_token(p)) for p in tokens[dot:] ) 
    return (rule.name.val, str_tokens, lookahead)

def pretty_lr1_set(rules: List[ast.Rule], lr1_set: Union[Lr1Set, Lr1FrSet]):
    out = []
    for item in lr1_set:
        out.append(pretty_lr1_item(rules, item))
    return out

def pretty_action(rules: List[ast.Rule], action: Action):
    if isinstance(action, Shift):
        return ("shift", action)
    if isinstance(action, Reduce):
        return ("reduce", rules[action[0]].prods[action[1]])