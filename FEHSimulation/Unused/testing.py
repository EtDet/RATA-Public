import re

def replace_atk(text: str) -> str:
    text = re.sub(r'(?<!\bATK)atk', 'def', text)
    text = re.sub(r'\battacker\b', 'defender', text, flags=re.IGNORECASE)
    return text

# Example usage
if __name__ == "__main__":

    test_string = '''    if "steadfast" in atkSkills and atkAllyWithin2Spaces:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5
        atkPenaltiesNeutralized[ATK] = True
        atkPenaltiesNeutralized[DEF] = True'''

    result = replace_atk(test_string)
    print(result)