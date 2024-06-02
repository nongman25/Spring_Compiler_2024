import sys

from build_table import build_table
from data_build import data_build
from grammer_rule_build import grammer_rule_build

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __str__(self):
        return self.value

def print_tree(node, level=0):
    print('  ' * level + str(node))
    for child in node.children:
        print_tree(child, level + 1)

def build_table(parsing_table, table_data, tokens, grammar_rules):
    lines = table_data.strip().split('\n')
    for line in lines:
        if not line.strip():
            continue
        parts = line.split(',')
        state = int(parts[0])  # 상태 번호
        actions = parts[1:]  # 해당 상태의 액션들

        state_dict = {}
        for token, action in zip(tokens, actions):
            if action:
                if action.startswith('s'):  # shift 동작
                    state_dict[token] = ('shift', int(action[1:]))
                elif action.startswith('r'):  # reduce 동작
                    rule_index = int(action[1:])
                    state_dict[token] = ('reduce', grammar_rules[rule_index])
                elif action == 'acc':  # accept 동작
                    state_dict[token] = 'accept'
                else:  # goto 동작
                    state_dict[token] = ('goto', int(action))
        parsing_table[state] = state_dict

def parsing_table_dictionary_build():
    parsing_table = {}
    table_data = data_build()
    tokens = token_build()
    grammar_rules = grammer_rule_build()
    build_table(parsing_table, table_data, tokens, grammar_rules)
    return parsing_table

def create_parsing_function(parsing_table, top_state, next_input_symbol, reductions, token_index):
    # 작업을 수행하는 함수들 정의
    def shift(next_state):
        def action(stack, tokens, parse_tree_stack):
            stack.append(next_state)
            token = tokens.pop(0)
            parse_tree_stack.append(TreeNode(token))  # 토큰을 트리 노드로 추가
            return "Shift performed. New state: {}".format(next_state)
        return action

    def reduce(production):
        def action(stack, tokens, parse_tree_stack):
            if production.split(" -> ")[1] == "''":
                num_items_to_pop = 0
            else:
                num_items_to_pop = len(production.split(" -> ")[1].split())
            lhs = production.split(" -> ")[0]

            new_node = TreeNode(lhs)  # 새로운 노드 생성
            for _ in range(num_items_to_pop):
                if stack:
                    stack.pop()
                    if parse_tree_stack:
                        new_node.add_child(parse_tree_stack.pop())  # 트리 노드를 자식으로 추가

            new_node.children.reverse()  # 자식 노드들의 순서를 역순으로 설정

            if stack:
                state_top = stack[-1]
            else:
                return "Error: Stack underflow during reduce."

            goto_action = parsing_table.get(state_top, {}).get(lhs, None)
            if goto_action is not None and isinstance(goto_action, tuple) and goto_action[0] == 'goto':
                next_state = goto_action[1]
                stack.append(next_state)
                parse_tree_stack.append(new_node)  # 새 노드를 트리 스택에 추가
                reductions.append(production)
                return "Reduce performed using production: {}. Go to state: {}".format(production, next_state)
            else:
                return "Error: No valid goto state found for {}.".format(lhs)
        return action

    def accept():
        def action(stack, tokens, parse_tree_stack):
            return "Parsing completed successfully."
        return action

    def goto(next_state):
        def action(stack, tokens, parse_tree_stack):
            stack.append(next_state)
            return "Go to state: {}".format(next_state)
        return action

    action_entry = parsing_table.get(top_state, {}).get(next_input_symbol, None)
    if action_entry is None:
        state_actions = parsing_table[top_state]
        symbols = list(state_actions.keys())
        print(f"Don't {next_input_symbol}. You need ", end='')
        for i, symbol in enumerate(symbols):
            print(f"{symbol}", end='')
            if i < len(symbols) - 1:
                print(", ", end='')
            else:
                print()
        return lambda stack, tokens, parse_tree_stack: "Error: No valid action for state {} with symbol '{}' at token index {}.".format(top_state, next_input_symbol, token_index)

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

    return lambda stack, tokens, parse_tree_stack: "Error: Action not defined for state {} with symbol '{}' at token index {}.".format(top_state, next_input_symbol, token_index)

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
    parse_tree_stack = []  # 파싱 트리 노드 스택
    reductions = []

    parsing_table = parsing_table_dictionary_build()
    tokens = input_string.split() + ["$"]

    print("Initial stack state:", stack)
    token_index = 0
    while tokens:
        next_input_symbol = tokens[0]
        parser_action = create_parsing_function(parsing_table, stack[-1], next_input_symbol, reductions, token_index)
        result = parser_action(stack, tokens, parse_tree_stack)
        print(result)
        if "Error" in result or result == "Parsing completed successfully.":
            break
        token_index += 1

    print("Final stack state:", stack)
    print("Reductions:", reductions)

    if parse_tree_stack:
        print("\nParse Tree:")
        print_tree(parse_tree_stack[-1])

if __name__ == "__main__":
    main()