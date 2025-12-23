
from analyzer.language_router import is_code

true_positives = [
    "def my_func():",
    "function test() { return 1; }",
    "class User {",
    "public static void main(String[] args)",
    "for (int i=0; i<10; i++)",
    "if __name__ == '__main__':",
    "import os",
    "console.log('hello')",
]

print(f"{'Code':<40} | {'Is Code?':<10}")
print("-" * 55)
for text in true_positives:
    result = is_code(text)
    print(f"{text:<40} | {str(result):<10}")
