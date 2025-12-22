# ==========================================================
# ALGORITHM → COMPLEXITY MAP (AUTHORITATIVE)
# Covers 20+ common algorithms with exact complexities
# ==========================================================

def resolve_complexity(pattern: str):
    """
    Maps detected algorithmic pattern to
    EXACT time & space complexity.
    """

    # =============== GRAPH ALGORITHMS ===============
    
    if pattern == "FLOYD_WARSHALL":
        # All-pairs shortest path: O(V³) time, O(V²) space for distance matrix
        return "O(V³)", "O(V²)"

    if pattern == "BELLMAN_FORD":
        # Single-source shortest path: V-1 iterations over all edges
        return "O(V × E)", "O(V)"

    if pattern == "DIJKSTRA":
        # Priority queue implementation with binary heap
        return "O(E log V)", "O(V + E)"

    if pattern == "KRUSKAL":
        # Sort edges + Union-Find with path compression
        return "O(E log E)", "O(V + E)"

    if pattern == "BFS":
        # Breadth-first search: visit each vertex and edge once
        return "O(V + E)", "O(V)"

    if pattern == "DFS":
        # Depth-first search: visit each vertex and edge once
        return "O(V + E)", "O(V)"

    if pattern == "GRAPH_TRAVERSAL":
        # Generic graph traversal (BFS/DFS)
        return "O(V + E)", "O(V)"

    # =============== SORTING ALGORITHMS ===============

    if pattern == "HEAP_SORT":
        # Build heap O(n) + n extractions O(log n) each
        return "O(n log n)", "O(log n)"

    if pattern == "MERGE_SORT":
        # Divide O(log n) levels × merge O(n) each level
        return "O(n log n)", "O(n)"

    if pattern == "QUICK_SORT":
        # Average case: O(n log n), but Worst-case (pathological) is O(n²)
        return "O(n²)", "O(log n)"

    if pattern == "SELECTION_SORT":
        # Nested loops: find minimum n times
        return "O(n²)", "O(1)"

    if pattern == "BUBBLE_SORT":
        # Nested loops: bubble up largest element
        return "O(n²)", "O(1)"

    if pattern == "QUADRATIC_SORT":
        # Generic quadratic sorting (Bubble/Insertion/Selection)
        return "O(n²)", "O(1)"

    # =============== SEARCH ALGORITHMS ===============

    if pattern == "BINARY_SEARCH":
        # Halve search space each iteration
        return "O(log n)", "O(1)"

    # =============== MATHEMATICAL ALGORITHMS ===============

    if pattern == "PRIME_CHECK":
        # Check divisibility up to sqrt(n)
        return "O(√n)", "O(1)"

    if pattern == "MATRIX_MULTIPLICATION":
        # Standard matrix multiplication: 3 nested loops
        return "O(n³)", "O(n²)"

    # =============== DYNAMIC PROGRAMMING ===============

    if pattern == "TSP_DP":
        # Held-Karp algorithm: bitmask DP
        return "O(n² × 2ⁿ)", "O(n × 2ⁿ)"

    if pattern == "SUBSET_SUM":
        # Recursive subset sum (exponential without memoization)
        return "O(2ⁿ)", "O(n)"

    # =============== COMBINATORIAL ===============

    if pattern == "PERMUTATION":
        # Generate all n! permutations
        return "O(n!)", "O(n)"

    # =============== ARRAY ALGORITHMS ===============

    if pattern == "KADANE":
        # Maximum subarray: single pass
        return "O(n)", "O(1)"

    if pattern == "FREQUENCY_COUNT":
        # Count frequencies using hash map
        return "O(n)", "O(n)"

    if pattern == "FIND_MAX_MIN":
        # Single pass to find max/min
        return "O(n)", "O(1)"

    if pattern == "CONSTANT_TIME":
        # No loops, no recursion - pure O(1)
        return "O(1)", "O(1)"

    # =============== RECURSION FALLBACKS ===============

    if pattern == "EXPONENTIAL_RECURSION":
        # Fibonacci-like multiple recursive calls
        return "O(2ⁿ)", "O(n)"

    if pattern == "LINEAR_RECURSION":
        # Single recursive call per invocation
        return "O(n)", "O(n)"

    # Unknown pattern - let rule engine handle it
    return None, None
