
from analyzer.language_router import is_code, detect_language

test_cases = [
    "This is a simple sentence.",
    "This should not show predictions.",
    "Hello world",
    "I am writing some text to test the analyzer.",
    "The complexity is O(n).",
    "def function(): pass", # Should be code
    "Class: Math", # Should be text
    "important notice", # Should be text
]

print(f"{'Text':<50} | {'Is Code?':<10} | {'Language':<10}")
print("-" * 80)
for text in test_cases:
    is_c = is_code(text)
    lang = detect_language(text)
    print(f"{text:<50} | {str(is_c):<10} | {lang:<10}")
