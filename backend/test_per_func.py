"""Simple test for per-function analyzer"""
from analyzer.per_function_analyzer import analyze_per_function

code = '''
def linear(arr):
    for x in arr:
        print(x)

def quadratic(arr):
    for i in arr:
        for j in arr:
            print(i, j)

def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

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

r = analyze_per_function(code)

print("=" * 50)
print("PER-FUNCTION ANALYSIS RESULTS")
print("=" * 50)

for f in r['functions']:
    print(f"\n{f['name']}():")
    print(f"  Time:  {f['timeComplexity']}")
    print(f"  Space: {f['spaceComplexity']}")
    print(f"  Reason: {f['reasoning']}")

print("\n" + "=" * 50)
print("WORST-CASE (using MAX, not multiply)")
print("=" * 50)
print(f"Worst Time:  {r['worstTime']} (from '{r['worstTimeFunction']}')")
print(f"Worst Space: {r['worstSpace']} (from '{r['worstSpaceFunction']}')")
print(f"Level: {r['complexityLevel']}")
print(f"Summary: {r['summary']}")
