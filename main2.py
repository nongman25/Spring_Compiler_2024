import sys

from build_table import build_table
from data_build import data_build
from grammer_rule_build import grammer_rule_build

class ParseTreeNode:
    def __init__(self, value, depth):
        self.value = value
        self.depth = depth
        self.children = []

def build_parse_tree(reductions):
    parse_tree = []
    depth=0
    for reduction in reductions[::-1]:
        lhs, rhs = reduction.split(" -> ")
        rhs_symbols = rhs.split()
        if depth == 0:
            parent = ParseTreeNode(lhs, depth)
            depth=depth+1
        else:
            for child in parent.children[::-1]:
                child
        for symbol in rhs_symbols:
            if symbol in token_build():  
                parent.children.append(ParseTreeNode(symbol, depth))
        parse_tree.append(parent)
    return parse_tree

def print_parse_tree(parse_tree, depth=0):
    for node in parse_tree:
        print("  " * depth + node.value + str(node.depth))
        if node.children:
            for child in node.children:
                print_parse_tree([child], depth + 1)

def parsing_table_dictionary_build():
    parsing_table = {}
    table_data = data_build()
    tokens = token_build()
    grammar_rules = grammer_rule_build()

    build_table(parsing_table, table_data, tokens, grammar_rules)
    #print(parsing_table)
    return parsing_table

def create_parsing_function(parsing_table, top_state, next_input_symbol, reductions, token_index):
    # 작업을 수행하는 함수들 정의
    def shift(next_state):
        def action(stack, tokens):
            stack.append(next_state)
            tokens.pop(0)  # 입력 토큰을 소비
            return "Shift performed. New state: {}".format(next_state)
        return action

    def reduce(production):
        def action(stack, tokens):
            if production.split(" -> ")[1] == "''":
                num_items_to_pop = 0
            else:
                num_items_to_pop = len(production.split(" -> ")[1].split())
            lhs = production.split(" -> ")[0]

            for _ in range(num_items_to_pop):
                if stack:
                    stack.pop()

            if stack:
                state_top = stack[-1]
            else:
                return "Error: Stack underflow during reduce."

            goto_action = parsing_table.get(state_top, {}).get(lhs, None)
            if goto_action is not None and isinstance(goto_action, tuple) and goto_action[0] == 'goto':
                next_state = goto_action[1]
                stack.append(next_state)
                reductions.append(production)
                return "Reduce performed using production: {}. Go to state: {}".format(production, next_state)
            else:
                return "Error: No valid goto state found for {}.".format(lhs)
        return action

    def accept():
        def action(stack, tokens):
            return "Parsing completed successfully."
        return action

    def goto(next_state):
        def action(stack, tokens):
            stack.append(next_state)
            return "Go to state: {}".format(next_state)
        return action

    action_entry = parsing_table.get(top_state, {}).get(next_input_symbol, None)
    if action_entry is None: # Why Error
        state_actions=parsing_table[top_state]
        symbols = list(state_actions.keys())
        print(f"Don't {next_input_symbol}. You need ",end='')
        for i, symbol in enumerate(symbols):
            print(f"{symbol}", end='')
            if i < len(symbols) - 1:
                print(", ", end='')
            else:
                print()
        return lambda stack, tokens: "Error: No valid action for state {} with symbol '{}' at token index {}.".format(top_state, next_input_symbol, token_index)

    if isinstance(action_entry, tuple):
        action_type, arg = action_entry
        if action_type == 'shift':
            return shift(arg)
        elif action_type == 'reduce':
            return reduce(arg)
        elif action_type == 'goto':
            return goto(arg)
    elif action_entry == 'accept':
        return accept()

    return lambda stack, tokens: "Error: Action not defined for state {} with symbol '{}' at token index {}.".format(top_state, next_input_symbol, token_index)

def token_build():
    tokens = [
        "vtype", "id", "semi", "assign", "literal", "character", "boolstr", 
        "addsub", "multdiv", "lparen", "rparen", "num", "lbrace", "rbrace", 
        "comma", "if", "while", "comp", "else", "return", "$", "S", "CODE", 
        "VDECL", "ASSIGN", "RHS", "EXPR", "TERM", "FACTOR", "FDECL", 
        "ARG", "MOREARGS", "BLOCK", "STMT", "COND", "BACKCOND", "ELSE", "RETURN"
    ]
    return tokens

def main():
    if len(sys.argv) != 2:
        print("Usage: python parser.py <input_file>")
        return

    input_file = sys.argv[1]
    try:
        with open(input_file, 'r') as file:
            input_string = file.read()
    except FileNotFoundError:
        print("Error: File not found.")
        return
    except IOError:
        print("Error: Could not read file.")
        return

    stack = [0]
    reductions = []

    parsing_table = parsing_table_dictionary_build()
    tokens = input_string.split() + ["$"]

    print("Initial stack state:", stack)
    token_index = 0
    while tokens:
        next_input_symbol = tokens[0]
        parser_action = create_parsing_function(parsing_table, stack[-1], next_input_symbol, reductions, token_index)
        result = parser_action(stack, tokens)
        print(result)
        if "Error" in result or result == "Parsing completed successfully.":
            break
        token_index += 1
    
    print("Final stack state:", stack)
    print("Reductions:", reductions)

    # 파싱 트리 구축
    #parse_tree = build_parse_tree(reductions)

    # 파싱 트리 출력
    #print("Parsing Tree:")
    #print_parse_tree(parse_tree)

if __name__ == "__main__":
    main()
