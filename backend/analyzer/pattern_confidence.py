# ==========================================================
# PATTERN CONFIDENCE VALIDATOR
# ==========================================================

from typing import Dict


class PatternConfidence:
    """
    Validates whether a detected pattern is CONFIDENT enough
    to override rule-based Big-O.
    """

    @staticmethod
    def is_confident(pattern: str, code: str, static: Dict) -> bool:
        code = code.lower()

        # =============== GRAPH ALGORITHMS ===============
        
        if pattern == "FLOYD_WARSHALL":
            return (
                static.get("maxLoopDepth", 0) >= 3
                and ("dist" in code or "matrix" in code)
            )

        if pattern == "BELLMAN_FORD":
            return (
                "bellman" in code or "ford" in code
                or (
                    "edge" in code
                    and "dist" in code
                    and static.get("maxLoopDepth", 0) >= 2
                )
            )

        if pattern == "DIJKSTRA":
            return (
                ("priorityqueue" in code or "heapq" in code or "heappush" in code or "priority_queue" in code)
                and ("dist" in code or "distance" in code)
            )

        if pattern == "KRUSKAL":
            return (
                ("kruskal" in code or ("union" in code and "find" in code))
                and "parent" in code
            )

        if pattern == "BFS":
            return (
                "queue" in code
                and ("visited" in code or "seen" in code)
                and ("adj" in code or "graph" in code or "neighbor" in code)
            )

        if pattern == "DFS":
            return (
                static.get("hasRecursion", False)
                and ("visited" in code or "seen" in code)
                and ("adj" in code or "graph" in code or "neighbor" in code)
            )

        if pattern == "GRAPH_TRAVERSAL":
            return (
                static.get("loopCount", 0) > 0
                and ("visited" in code or "seen" in code)
                and ("graph" in code or "adj" in code)
            )

        # =============== SORTING ALGORITHMS ===============

        if pattern == "HEAP_SORT":
            return (
                "heapsort" in code or "heap_sort" in code or "heapify" in code
                or ("heap" in code and ("largest" in code or "smallest" in code))
            )

        if pattern == "MERGE_SORT":
            return (
                static.get("hasRecursion", False)
                and "merge" in code
            )

        if pattern == "QUICK_SORT":
            return (
                static.get("hasRecursion", False)
                and ("pivot" in code or "partition" in code)
            )

        if pattern == "SELECTION_SORT":
            return (
                static.get("maxLoopDepth", 0) == 2
                and ("min_idx" in code or "min_index" in code or "minidx" in code)
            )

        if pattern == "BUBBLE_SORT":
            return (
                static.get("maxLoopDepth", 0) == 2
                and ("bubble" in code or "swapped" in code)
            )

        if pattern == "QUADRATIC_SORT":
            return (
                static.get("maxLoopDepth", 0) == 2
                and ("swap" in code or "temp" in code)
            )

        # =============== SEARCH ALGORITHMS ===============

        if pattern == "BINARY_SEARCH":
            return (
                "mid" in code
                and ("low" in code or "left" in code or "lo" in code or "start" in code)
                and ("high" in code or "right" in code or "hi" in code or "end" in code)
                and (static.get("hasLogLoop", False) or static.get("hasRecursion", False) or "while" in code)
            )

        # =============== MATHEMATICAL ALGORITHMS ===============

        if pattern == "PRIME_CHECK":
            return (
                ("prime" in code or "isprime" in code or "is_prime" in code)
                or ("sqrt" in code and "%" in code)
            )

        if pattern == "MATRIX_MULTIPLICATION":
            return (
                static.get("maxLoopDepth", 0) >= 3
                and ("matrix" in code or "][" in code)
            )

        # =============== DYNAMIC PROGRAMMING ===============

        if pattern == "TSP_DP":
            return (
                ("tsp" in code or "traveling" in code or "travelling" in code or "salesman" in code)
                or ("mask" in code and "dp" in code and ("1 <<" in code or "1<<" in code))
            )

        if pattern == "SUBSET_SUM":
            return (
                "subset" in code
                and ("sum" in code or "target" in code)
            )

        # =============== COMBINATORIAL ===============

        if pattern == "PERMUTATION":
            return (
                ("permut" in code or "generate" in code)
                and static.get("hasRecursion", False)
            )

        # =============== ARRAY ALGORITHMS ===============

        if pattern == "KADANE":
            return (
                "kadane" in code
                or ("max_so_far" in code or "maxsofar" in code)
                or ("current_max" in code or "currentmax" in code)
                or "max_ending" in code
            )

        if pattern == "FREQUENCY_COUNT":
            return (
                ("frequency" in code or "freq" in code or "count" in code)
                and ("map" in code or "dict" in code or "hash" in code or "{}" in code)
            )

        if pattern == "FIND_MAX_MIN":
            return (
                ("findmax" in code or "findmin" in code or "find_max" in code or "find_min" in code)
                or ("maxval" in code or "minval" in code or "max_val" in code or "min_val" in code)
                or ("maxelement" in code or "minelement" in code)
                or (
                    ("max" in code or "min" in code)
                    and static.get("maxLoopDepth", 0) == 1
                    and static.get("loopCount", 0) == 1
                )
            )

        if pattern == "CONSTANT_TIME":
            return (
                static.get("loopCount", 0) <= 1
                and static.get("maxLoopDepth", 0) == 0
                and not static.get("hasRecursion", False)
            )

        # =============== RECURSION FALLBACKS ===============

        if pattern == "EXPONENTIAL_RECURSION":
            return static.get("multiRecursion", False)

        if pattern == "LINEAR_RECURSION":
            return (
                static.get("hasRecursion", False)
                and not static.get("multiRecursion", False)
            )

        return False
