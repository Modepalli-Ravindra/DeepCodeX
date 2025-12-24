
# ==========================================
# STANDARD LIB COMPLEXITY KNOWLEDGE BASE
# ==========================================
# Maps function calls to their intrinsic time complexity.
# Used when Taint Analysis confirms the arguments are scaling.

METHOD_COMPLEXITY_MAP = {
    # PYTHON LIST
    "append": "O(1)",
    "pop": "O(1)",         # Optimistic (pop from end)
    "pop(0)": "O(n)",      # Specific check needed in logic
    "insert": "O(n)",
    "remove": "O(n)",
    "index": "O(n)",
    "count": "O(n)",
    "sort": "O(n log n)",
    "reverse": "O(n)",
    "extend": "O(k)",     # k is len of extension

    # PYTHON SET/DICT
    "add": "O(1)",
    "get": "O(1)",
    "set": "O(1)",
    "has_key": "O(1)",
    "contains": "O(1)",
    "copy": "O(n)",

    # PYTHON STRING
    "find": "O(n)",
    "replace": "O(n)",
    "split": "O(n)",
    "join": "O(n)",

    # HEAPQ
    "heappush": "O(log n)",
    "heappop": "O(log n)",
    "heapify": "O(n)",
    "nlargest": "O(n log k)",
    "nsmallest": "O(n log k)",

    # BISECT (Binary Search)
    "bisect": "O(log n)",
    "bisect_left": "O(log n)",
    "bisect_right": "O(log n)",
    "insort": "O(n)", # Insertion is O(n) even if finding is log n

    # MATH
    "factorial": "O(n)",
    "sqrt": "O(1)", # for our purposes, arithmetic is O(1)
    "pow": "O(1)",
}
