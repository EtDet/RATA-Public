def transform_string(input_str):
    lines = input_str.split('\n')

    transformed_lines = []
    for line in lines:
        leading_whitespace = ''
        for char in line:
            if char.isspace():
                leading_whitespace += char
            else:
                break
        content = line[len(leading_whitespace):]

        if not content.strip():
            transformed_lines.append(line)
            continue

        words = content.split()

        transformed_words = []
        for word in words:
            if word == "attacker":
                transformed_words.append("defender")
            elif word == "defender":
                transformed_words.append("attacker")
            else:
                transformed_words.append(word)

        temp_result = " ".join(transformed_words)
        words = temp_result.split()

        result_words = []
        for word in words:
            if word.isupper():
                result_words.append(word)
            else:
                if word == "def":
                    result_words.append("atk")
                elif word == "atk":
                    result_words.append("def")
                elif "def" in word and word != "defender":
                    result_words.append(word.replace("def", "atk"))
                elif "atk" in word:
                    result_words.append(word.replace("atk", "def"))
                else:
                    result_words.append(word)

        transformed_line = leading_whitespace + " ".join(result_words)
        transformed_lines.append(transformed_line)

    return '\n'.join(transformed_lines)

text = ''' if "SUPER FREAKING MARIO!" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.DR_first_strikes_NSP.append(40)
        atkr.true_stat_damages.append((SPD, 20))
        atkr.all_hits_heal += 7'''

print(transform_string(text))
