import re
from typing import Dict, Optional, List, Tuple


# Complexity ordering for comparison
COMPLEXITY_ORDER = {
    "CONSTANT_TIME": 0,
    "FIND_MAX_MIN": 1,
    "BINARY_SEARCH": 2,
    "FREQUENCY_COUNT": 3,
    "LINEAR_RECURSION": 4,
    "KADANE": 5,
    "BFS": 6,
    "DFS": 7,
    "GRAPH_TRAVERSAL": 8,
    "PRIME_CHECK": 9,
    "MERGE_SORT": 10,
    "HEAP_SORT": 11,
    "QUICK_SORT": 12,
    "DIJKSTRA": 13,
    "BELLMAN_FORD": 14,
    "SELECTION_SORT": 15,
    "BUBBLE_SORT": 16,
    "QUADRATIC_SORT": 17,
    "MATRIX_MULTIPLICATION": 18,
    "FLOYD_WARSHALL": 19,
    "KRUSKAL": 20,
    "TSP_DP": 21,
    "SUBSET_SUM": 22,
    "EXPONENTIAL_RECURSION": 23,
    "PERMUTATION": 24,
}


class PatternAnalyzer:
    """
    Detects algorithmic patterns and returns the DOMINANT (highest complexity) pattern.
    Covers 20+ common algorithms with accurate detection.
    """

    def __init__(self, code: str, static: Dict):
        self.code = code.lower()
        self.original_code = code
        self.static = static

    def detect(self) -> Optional[str]:
        """
        Find all matching patterns and return the one with HIGHEST complexity.
        This ensures large codebases with multiple algorithms report the dominant one.
        """
        detected_patterns: List[str] = []
        
        # =============== GRAPH ALGORITHMS ===============
        if self._is_floyd_warshall():
            detected_patterns.append("FLOYD_WARSHALL")
        
        if self._is_bellman_ford():
            detected_patterns.append("BELLMAN_FORD")
        
        if self._is_dijkstra():
            detected_patterns.append("DIJKSTRA")
        
        if self._is_kruskal():
            detected_patterns.append("KRUSKAL")
        
        if self._is_bfs():
            detected_patterns.append("BFS")
        
        if self._is_dfs():
            detected_patterns.append("DFS")
        
        if self._is_graph_traversal():
            detected_patterns.append("GRAPH_TRAVERSAL")

        # =============== SORTING ALGORITHMS ===============
        if self._is_heap_sort():
            detected_patterns.append("HEAP_SORT")
        
        if self._is_merge_sort():
            detected_patterns.append("MERGE_SORT")

        if self._is_quick_sort():
            detected_patterns.append("QUICK_SORT")
        
        if self._is_selection_sort():
            detected_patterns.append("SELECTION_SORT")
        
        if self._is_bubble_sort():
            detected_patterns.append("BUBBLE_SORT")
        
        if self._is_quadratic_sort():
            detected_patterns.append("QUADRATIC_SORT")

        # =============== SEARCH ALGORITHMS ===============
        if self._is_binary_search():
            detected_patterns.append("BINARY_SEARCH")

        # =============== MATHEMATICAL ALGORITHMS ===============
        if self._is_prime_check():
            detected_patterns.append("PRIME_CHECK")
        
        if self._is_matrix_multiplication():
            detected_patterns.append("MATRIX_MULTIPLICATION")

        # =============== DYNAMIC PROGRAMMING ===============
        if self._is_tsp_dp():
            detected_patterns.append("TSP_DP")
        
        if self._is_subset_sum():
            detected_patterns.append("SUBSET_SUM")

        # =============== COMBINATORIAL ===============
        if self._is_permutation():
            detected_patterns.append("PERMUTATION")

        # =============== ARRAY ALGORITHMS ===============
        if self._is_kadane():
            detected_patterns.append("KADANE")
        
        if self._is_frequency_count():
            detected_patterns.append("FREQUENCY_COUNT")
        
        if self._is_find_max_min():
            detected_patterns.append("FIND_MAX_MIN")
        
        if self._is_constant_time():
            detected_patterns.append("CONSTANT_TIME")

        # =============== RECURSION FALLBACKS ===============
        if self._is_exponential_recursion():
            detected_patterns.append("EXPONENTIAL_RECURSION")

        if self._is_linear_recursion():
            detected_patterns.append("LINEAR_RECURSION")

        # Return the pattern with HIGHEST complexity
        if not detected_patterns:
            return None
        
        # Sort by complexity order (highest first) and return the dominant one
        detected_patterns.sort(key=lambda p: COMPLEXITY_ORDER.get(p, 0), reverse=True)
        return detected_patterns[0]

    def detect_all(self) -> List[str]:
        """Return all detected patterns (for debugging/detailed output)."""
        detected = []
        
        for method_name in dir(self):
            if method_name.startswith('_is_') and method_name != '_is_constant_time':
                method = getattr(self, method_name)
                if callable(method) and method():
                    pattern_name = method_name[4:].upper()
                    detected.append(pattern_name)
        
        return detected

    # ================== GRAPH ALGORITHMS ==================

    def _is_floyd_warshall(self) -> bool:
        """Triple nested loop with k,i,j pattern for all-pairs shortest path."""
        return (
            self.static.get("maxLoopDepth", 0) >= 3
            and re.search(r"dist\s*\[", self.code)
            and (re.search(r"dist\s*\[\s*\w+\s*\]\s*\[\s*\w+\s*\]", self.code) or "inf" in self.code)
        )

    def _is_bellman_ford(self) -> bool:
        """V-1 iterations over all edges."""
        return (
            re.search(r"bellman|ford", self.code)
            or (
                re.search(r"edge", self.code)
                and re.search(r"dist", self.code)
                and self.static.get("maxLoopDepth", 0) >= 2
                and ("integer.max_value" in self.code or "int_max" in self.code or "inf" in self.code)
            )
        )

    def _is_dijkstra(self) -> bool:
        """Priority queue/heap with distance relaxation."""
        return (
            re.search(r"priorityqueue|heapq|heappush|heappop|minheap|priority_queue", self.code)
            and re.search(r"dist|distance", self.code)
        )

    def _is_kruskal(self) -> bool:
        """Union-Find with edge sorting for MST."""
        return (
            (re.search(r"kruskal", self.code) or re.search(r"union|find", self.code))
            and re.search(r"parent", self.code)
            and re.search(r"edge|weight", self.code)
        )

    def _is_bfs(self) -> bool:
        """Queue-based graph traversal."""
        return (
            re.search(r"queue", self.code)
            and re.search(r"visited|seen", self.code)
            and re.search(r"adj|graph|neighbor", self.code)
        )

    def _is_dfs(self) -> bool:
        """Recursive or stack-based graph traversal."""
        has_vis = re.search(r"visited|seen|used|marked|is_visited|found", self.code)
        has_adj = re.search(r"adj|graph|neighbor|edges|connection|link", self.code)
        return self.static.get("hasRecursion", False) and has_vis and has_adj

    def _is_graph_traversal(self) -> bool:
        """Generic graph traversal (BFS/DFS)."""
        has_vis = re.search(r"visited|seen|used|marked", self.code)
        has_adj = re.search(r"graph|adj|edges|nodes", self.code)
        return has_vis and has_adj

    # ================== SORTING ALGORITHMS ==================

    def _is_heap_sort(self) -> bool:
        """Heapify pattern with in-place sorting."""
        return (
            re.search(r"heapsort|heap_sort|heapify", self.code)
            or (
                re.search(r"heap", self.code)
                and re.search(r"largest|smallest", self.code)
            )
        )

    def _is_merge_sort(self) -> bool:
        """Divide and conquer with merge."""
        return (
            self.static.get("hasRecursion", False)
            and re.search(r"merge", self.code)
            and re.search(r"left|right|mid", self.code)
        )

    def _is_quick_sort(self) -> bool:
        """Pivot-based partitioning."""
        return (
            self.static.get("hasRecursion", False)
            and (re.search(r"pivot", self.code) or re.search(r"partition", self.code))
        )

    def _is_selection_sort(self) -> bool:
        """Find minimum in unsorted portion."""
        return (
            self.static.get("maxLoopDepth", 0) >= 2
            and re.search(r"min_idx|min_index|minidx|minindex", self.code)
            and re.search(r"swap|temp", self.code)
        )

    def _is_bubble_sort(self) -> bool:
        """Adjacent element comparison and swap."""
        return (
            self.static.get("maxLoopDepth", 0) >= 2
            and (re.search(r"bubble", self.code) or re.search(r"swapped", self.code))
            and re.search(r"swap|temp", self.code)
        )

    def _is_quadratic_sort(self) -> bool:
        """Generic O(n²) sorting pattern with nested loops."""
        return (
            self.static.get("maxLoopDepth", 0) >= 2
            and re.search(r"swap|temp", self.code)
            and re.search(r"arr|list|array|data", self.code)
            and self.static.get("loopCount", 0) >= 2
        )

    # ================== SEARCH ALGORITHMS ==================

    def _is_binary_search(self) -> bool:
        """Binary search with left/right/mid pointers."""
        # More strict: requires the division by 2 pattern
        has_mid = re.search(r"mid", self.code)
        has_left_right = (re.search(r"left|low|lo", self.code)) and (re.search(r"right|high|hi", self.code))
        has_halving = re.search(r"/\s*2|//\s*2|>>\s*1", self.code)
        
        return has_mid and has_left_right and has_halving

    # ================== MATHEMATICAL ALGORITHMS ==================

    def _is_prime_check(self) -> bool:
        """Prime number checking with sqrt optimization."""
        return (
            re.search(r"prime|isprime|is_prime", self.code)
            or (
                re.search(r"sqrt|math\.sqrt", self.code)
                and re.search(r"%\s*\d|%\s*i|mod", self.code)
            )
        )

    def _is_matrix_multiplication(self) -> bool:
        """Matrix multiplication with triple nested loops."""
        has_triple_loop = self.static.get("maxLoopDepth", 0) >= 3
        has_matrix_keyword = re.search(r"matrix|matri|multiply|multipl", self.code)
        has_2d_array_pattern = re.search(r"\[\s*\w+\s*\]\s*\[\s*\w+\s*\]", self.code)
        has_accumulation = re.search(r"\+=", self.code)
        
        return (
            has_triple_loop
            and (has_matrix_keyword or (has_2d_array_pattern and has_accumulation))
        )

    # ================== DYNAMIC PROGRAMMING ==================

    def _is_tsp_dp(self) -> bool:
        """Traveling Salesman Problem with bitmask DP."""
        return (
            re.search(r"tsp|traveling|travelling|salesman", self.code)
            or (
                re.search(r"mask|1\s*<<", self.code)
                and re.search(r"dp\s*\[", self.code)
                and re.search(r"dist|cost", self.code)
            )
        )

    def _is_subset_sum(self) -> bool:
        """Subset sum with recursion or DP."""
        return (
            re.search(r"subset", self.code)
            and re.search(r"sum|target", self.code)
            and self.static.get("hasRecursion", False)
        )

    # ================== COMBINATORIAL ==================

    def _is_permutation(self) -> bool:
        """Generating all permutations."""
        return (
            re.search(r"permut|generate", self.code)
            and self.static.get("hasRecursion", False)
            and re.search(r"str|char|swap", self.code)
        )

    # ================== ARRAY ALGORITHMS ==================

    def _is_kadane(self) -> bool:
        """Kadane's algorithm for maximum subarray."""
        return (
            re.search(r"kadane|max_so_far|maxsofar|current_max|currentmax|max_ending", self.code)
            or (
                re.search(r"max", self.code)
                and re.search(r"current|curr", self.code)
                and self.static.get("maxLoopDepth", 0) == 1
            )
        )

    def _is_frequency_count(self) -> bool:
        """Character/element frequency counting."""
        return (
            re.search(r"frequency|freq|count", self.code)
            and (re.search(r"map|dict|hash|object", self.code))
            and self.static.get("maxLoopDepth", 0) == 1
        )

    def _is_find_max_min(self) -> bool:
        """Finding maximum or minimum element."""
        return (
            re.search(r"findmax|findmin|find_max|find_min|maxval|minval|max_val|min_val|maxelement|minelement", self.code)
            or (
                re.search(r"max|min", self.code)
                and self.static.get("maxLoopDepth", 0) == 1
                and self.static.get("loopCount", 0) == 1
                and not self.static.get("hasRecursion", False)
            )
        )

    def _is_constant_time(self) -> bool:
        """O(1) operations - no loops, no recursion."""
        return (
            self.static.get("loopCount", 0) <= 1
            and self.static.get("maxLoopDepth", 0) == 0
            and not self.static.get("hasRecursion", False)
        )

    # ================== RECURSION FALLBACKS ==================

    def _is_exponential_recursion(self) -> bool:
        """Multiple recursive calls (exponential)."""
        return self.static.get("multiRecursion", False)

    def _is_linear_recursion(self) -> bool:
        """Single recursive call (linear)."""
        return self.static.get("hasRecursion", False) and not self.static.get("multiRecursion", False)
