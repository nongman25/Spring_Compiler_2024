def build_table(parsing_table, table_data, tokens,grammar_rules):
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