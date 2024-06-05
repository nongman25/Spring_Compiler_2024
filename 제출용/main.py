import sys

from build_table import build_table # 파싱 테이블 생성
from data_build import data_build # SLR-parsing table 데이터
from grammer_rule_build import grammer_rule_build # CFG 문법 규칙

# 파싱 트리를 만들기 위한 트리 구조
class TreeNode: 
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __str__(self):
        return self.value

# 파싱 트리 출력
def print_tree(node, level=0, prefix=""): 
    lead = " " * (level * 4)
    if level > 0:
        lead += "|-- "

    print(f"{lead}{prefix}{node.value}")

    if node.children:   
        if len(node.children) == 1:
            print_tree(node.children[0], level + 1, "`-")
        else:
            for child in node.children[:-1]:
                print_tree(child, level + 1, "|-")
            print_tree(node.children[-1], level + 1, "`-")

# 파싱 테이블을 생성
def parsing_table_dictionary_build(): 
    parsing_table = {}
    table_data = data_build()
    tokens = token_build()
    grammar_rules = grammer_rule_build()
    build_table(parsing_table, table_data, tokens, grammar_rules)
    return parsing_table

# 파싱 테이블에 따라 동작을 정의
def create_parsing_function(parsing_table, top_state, next_input_symbol, reductions, token_index): 
    # Shift 동작 정의
    def shift(next_state): 
        def action(stack, tokens, parse_tree_stack):
            stack.append(next_state)
            token = tokens.pop(0)
            parse_tree_stack.append(TreeNode(token))  
            return "Shift performed. New state: {}".format(next_state)
        return action

    # Reduce 동작 정의
    def reduce(production):
        def action(stack, tokens, parse_tree_stack):
            # production을 분석하여 필요한 요소 수를 파악
            if production.split(" -> ")[1] == "''":
                num_items_to_pop = 0
            else:
                num_items_to_pop = len(production.split(" -> ")[1].split())
            lhs = production.split(" -> ")[0]

            new_node = TreeNode(lhs)  
            # 스택에서 상태 제거
            for _ in range(num_items_to_pop):
                if stack:
                    stack.pop()
                    if parse_tree_stack:
                        new_node.add_child(parse_tree_stack.pop()) 

            new_node.children.reverse()  

            # 이전의 top 상태
            if stack:
                state_top = stack[-1]
            else:
                return "Error: Stack underflow during reduce."

            # GOTO 작업을 찾아 스택에 새 상태를 추가
            goto_action = parsing_table.get(state_top, {}).get(lhs, None)
            if goto_action is not None and isinstance(goto_action, tuple) and goto_action[0] == 'goto':
                next_state = goto_action[1]
                stack.append(next_state)
                parse_tree_stack.append(new_node)  
                reductions.append(production)
                return "Reduce performed using production: {}. Go to state: {}".format(production, next_state)
            else:
                return "Error: No valid goto state found for {}.".format(lhs)
        return action

    # Accept 동작 정의
    def accept():
        def action(stack, tokens, parse_tree_stack):
            return "Parsing completed successfully."
        return action

    # Goto 동작 정의
    def goto(next_state):
        def action(stack, tokens, parse_tree_stack):
            stack.append(next_state)
            return "Go to state: {}".format(next_state)
        return action
    
    # 테이블에서 동작 결정
    action_entry = parsing_table.get(top_state, {}).get(next_input_symbol, None)
    if action_entry is None:
        state_actions = parsing_table[top_state]
        symbols = list(state_actions.keys())
        print(f"You should use {symbols} instead of {next_input_symbol}")
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

# 토큰들의 집합
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
    parse_tree_stack = [] 
    reductions = [] 

    parsing_table = parsing_table_dictionary_build()
    tokens = input_string.split() + ["$"]

    print("Initial stack state:", stack)
    token_index = 0
    Success=False
    # 분리한 토큰들을 사용하여 구문 분석을 수행하는 과정
    while tokens:
        next_input_symbol = tokens[0]
        parser_action = create_parsing_function(parsing_table, stack[-1], next_input_symbol, reductions, token_index)
        result = parser_action(stack, tokens, parse_tree_stack)
        print(result)
        if "Error" in result or result == "Parsing completed successfully.":
            if result == "Parsing completed successfully." :
                Success=True
            break
        token_index += 1

    print("Final stack state:", stack)
    print("Reductions:", reductions)

    if parse_tree_stack and Success:
        print("\nParse Tree:")
        print_tree(parse_tree_stack[-1])

if __name__ == "__main__":
    main()