import sys
import pprint

from descr_parser import parse
import descr_ast as ast
import grammar

from typing import Set, Iterable, List

def make_flags(args: List[str], all_flags: Iterable[str]):
    found_args = set()
    for flag in args:
        assert flag.startswith('--')
        found_args.add(flag[2:])
    return { f: f in found_args for f in all_flags }

def produce_ast(args):
    filename = args[0]
    flags = make_flags(args[1:], {
        "debug_lexer"
    })

    with open(filename) as file:
        ast = parse(file, **flags)
        pprint.pprint(ast)

def produce_graph(args):
    filename = args[0]
    assert not args[1:]
    with open(filename) as file:
        parsed_ast = parse(file)
        
        rules = ast.ast_rules(parsed_ast)
        states, actions = grammar.make_graph(rules, 0)
        
        print("=== LR1 Parsing Sets ===")
        for i in states.a_iter():
            state = states.get_a(i)
            print(f"State {i}:\n  ", end='')
            pprint.pprint(grammar.pretty_lr1_set(rules, state), indent=2)
        
        print()

        print("=== Actions ===")
        for i, s in enumerate(actions):
            print(f"State {i}: ", end='')
            pprint.pprint({ tok: grammar.pretty_action(rules, action) for tok, action in s.items() })

def main():
    args = sys.argv[1:]
    if args[0] == "ast":
        produce_ast(args[1:])
    elif args[0] == "graph":
        produce_graph(args[1:])
    else:
        raise RuntimeError(f"Unknown argument {args[0]}!")

if __name__ == "__main__":
    main()