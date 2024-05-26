import sys

def create_parsing_function(top_state, next_input_symbol,reductions):
    # 파싱 테이블 정의
    parsing_table = {
        0: {'A': ('goto', 1), 'a': ('shift', 2)},
        1: {'B': ('goto', 3), '$':'accept', 'id': ('shift', 4)},
        2: {'id': ('reduce', 'A -> a'), '$': ('reduce', 'A -> a')},
        4: {'id': ('reduce', 'B -> id'), '$': ('reduce', 'B -> id')},
        3: {'id': ('reduce', 'A -> A B'), '$': ('reduce', 'A -> A B')}
    }

    # 작업을 수행하는 함수들 정의
    def shift(next_state):
        def action(stack, tokens):
            stack.append(next_state)
            tokens.pop(0)  # 입력 토큰을 소비
            return "Shift performed. New state: {}".format(next_state)
        return action

    def reduce(production):
        def action(stack, tokens):
            # production을 분석하여 필요한 요소 수를 파악
            # 예: 'A -> a B'인 경우 2개의 요소를 스택에서 pop
            num_items_to_pop = len(production.split(" -> ")[1].split())
            lhs = production.split(" -> ")[0]

            # 스택에서 상태를 제거
            for _ in range(num_items_to_pop):
                if stack:
                    stack.pop()

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
                reductions.append(production)
                return "Reduce performed using production: {}. Go to state: {}".format(production, next_state)
            else:
                return "Error: No valid goto state found."
        return action

#    def reduce(production):
#        def action(stack, tokens):
#            # 여기서는 실제 문법에 따른 구현이 필요
#            return "Reduce performed using production: {}".format(production)
#        return action

    def accept():
        def action(stack, tokens):
            return "Parsing completed successfully."
        return action

    def goto(next_state):
        def action(stack, tokens):
            stack.append(next_state)
            return "Go to state: {}".format(next_state)
        return action

    # 테이블에서 동작 결정
    action_entry = parsing_table.get(top_state, {}).get(next_input_symbol, None)
    if action_entry is None:
        return lambda stack, tokens: "Error: No valid action."

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

    return lambda stack, tokens: "Error: Action not defined."

def main():
    if len(sys.argv) != 2:
        print("use right argument")
        return

    input_file = sys.argv[1]
    input_string = "default"
    try:
        with open(input_file, 'r') as file:
            input_string = file.read()
    except FileNotFoundError:
        print("Error: File not found.")
        return
    except IOError:
        print("Error: Could not read file.")
        return

    stack = []

    stack.append(0)
    reductions = []
    
    print("Initial stack state:", stack)
    next_input_symbol_index = 0
    tokens = input_string.split(" ")
    tokens.append("$")
    while tokens.count != 0:
        parser_action = create_parsing_function(stack[-1],tokens[next_input_symbol_index],reductions)
        result = parser_action(stack, tokens)
        print(result)
        if "Error" in result or result == "Parsing completed successfully.":
            break

    print("Reductions:", reductions)

if __name__ == "__main__":
    main()
