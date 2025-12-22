"""Debug plain text detection"""
from analyzer.language_router import detect_language, is_code

# The exact text from the user
text = '''Your "overall time & space complexity" problem has design issues, not math issues.
Here's what's wrong and exactly how to solve it.

❌ ISSUE 1: "Overall Complexity" ITSELF IS A BROKEN CONCEPT

A file like yours has:

sorting

DP

graph

recursion

matrix ops

There is NO single Big-O for that.

So when your system outputs:

O(n!)

or O(n)

…it's invalid by definition.

✅ FIX

Stop computing overall complexity as a single value.

Replace it with:

Per-function complexity

Worst-case detected complexity

❌ ISSUE 2: You are COLLAPSING ALL FUNCTIONS INTO ONE AST TREE

What you're probably doing:

counting total loops

counting recursion

counting depth

feeding to LLM / rules

guessing one Big-O

That's why factorial shows up.

✅ FIX

Split analysis into FUNCTION SCOPES

Algorithm:

For each function:
  build AST
  detect loops / recursion
  compute complexity independently


Never mix functions.

❌ ISSUE 3: You treat ANY recursion as factorial/exponential

This is a classic analyzer mistake.

You likely have logic like:

if recursion && loop:
   O(n!)


That is WRONG.

✅ FIX: Proper recursion classification
Pattern	Correct Big-O
f(n-1)	O(n)
f(n-1)+f(n-2)	O(2ⁿ)
permutation swap recursion	O(n!)
divide recursion n/2	O(log n)
merge recursion	O(n log n)

Factorial only when recursion depth multiplies problem size, not when recursion exists.'''

print("=" * 50)
print("DEBUG: Plain Text Detection")
print("=" * 50)
print(f"\nText length: {len(text)} chars")
print(f"Lines: {len(text.split(chr(10)))}")

# Test is_code function
result = is_code(text)
print(f"\nis_code() result: {result}")

# Test detect_language function  
lang = detect_language(text)
print(f"detect_language() result: {lang}")

# Debug: count prose vs code lines
lines = text.strip().split('\n')
non_empty = [l.strip() for l in lines if l.strip()]

print(f"\nNon-empty lines: {len(non_empty)}")
print("\nFirst 10 lines:")
for i, l in enumerate(non_empty[:10]):
    print(f"  {i+1}: {l[:60]}...")
