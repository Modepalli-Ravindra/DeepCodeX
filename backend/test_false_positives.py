
from analyzer.language_router import is_code

false_positives_candidates = [
    "function of x is y",
    "class of 2024",
    "definitely not code",
    "public transport",
    "private investigator",
    "void where prohibited",
    "int values are numbers",
    "import goods from china",
    "from start to finish",
    "if I go to the store",
    "try to do this",
    "switch to geico",
]

print(f"{'Text':<30} | {'Is Code?':<10}")
print("-" * 45)
for text in false_positives_candidates:
    result = is_code(text)
    print(f"{text:<30} | {str(result):<10}")
