"""Test plain text detection"""
import requests

API = 'http://127.0.0.1:5000/analyze'

# The exact text from the user's screenshot
plain_text = '''
// Paste your code here
function example() {
  return "Hello World";
}
Your "overall time & space complexity" problem has design issues, not math issues.

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

...it's invalid by definition.

✅ FIX

Stop computing overall complexity as a single value.

Replace it with:

Per-function complexity

Worst-case detected complexity

❌ ISSUE 2: You are COLLAPSING ALL FUNCTIONS INTO ONE AST TREE

What you're probably doing:

counting total loops
'''

# Real Python code for comparison
real_python = '''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
'''

def test(name, code, expected_is_code):
    try:
        r = requests.post(API, json={'code': code}, timeout=30)
        result = r.json()
        lang = result.get('language', 'Unknown')
        is_code = result.get('isCode', True)
        
        # Check if detected as plain text
        detected_as_text = (lang == "Plain Text" or is_code == False)
        
        passed = (not expected_is_code and detected_as_text) or (expected_is_code and not detected_as_text)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
        print(f"  Language: {lang}")
        print(f"  isCode: {is_code}")
        print(f"  Expected text: {not expected_is_code}")
        print()
        return passed
    except Exception as e:
        print(f"{name}: ❌ ERROR - {e}")
        return False

print("=" * 50)
print("PLAIN TEXT vs CODE DETECTION TEST")
print("=" * 50)
print()

results = []
results.append(test("Plain Text (from screenshot)", plain_text, expected_is_code=False))
results.append(test("Real Python Code", real_python, expected_is_code=True))

print("=" * 50)
print(f"Results: {sum(results)}/{len(results)} passed")
