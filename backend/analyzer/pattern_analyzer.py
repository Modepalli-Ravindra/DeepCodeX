import re
from typing import Dict, Optional


class PatternAnalyzer:
    """
    Detects POSSIBLE algorithmic patterns.
    Covers 20+ common algorithms with accurate detection.
    """

    def __init__(self, code: str, static: Dict):
        self.code = code.lower()
        self.original_code = code
        self.static = static

    def detect(self) -> Optional[str]:
        """Priority order matters - more specific patterns first."""
        
        # =============== GRAPH ALGORITHMS ===============
        if self._is_floyd_warshall():
            return "FLOYD_WARSHALL"
        
        if self._is_bellman_ford():
            return "BELLMAN_FORD"
        
        if self._is_dijkstra():
            return "DIJKSTRA"
        
        if self._is_kruskal():
            return "KRUSKAL"
        
        if self._is_bfs():
            return "BFS"
        
        if self._is_dfs():
            return "DFS"
        
        if self._is_graph_traversal():
            return "GRAPH_TRAVERSAL"

        # =============== SORTING ALGORITHMS ===============
        if self._is_heap_sort():
            return "HEAP_SORT"
        
        if self._is_merge_sort():
            return "MERGE_SORT"

        if self._is_quick_sort():
            return "QUICK_SORT"
        
        if self._is_selection_sort():
            return "SELECTION_SORT"
        
        if self._is_bubble_sort():
            return "BUBBLE_SORT"
        
        if self._is_quadratic_sort():
            return "QUADRATIC_SORT"

        # =============== SEARCH ALGORITHMS ===============
        if self._is_binary_search():
            return "BINARY_SEARCH"

        # =============== MATHEMATICAL ALGORITHMS ===============
        if self._is_prime_check():
            return "PRIME_CHECK"
        
        if self._is_matrix_multiplication():
            return "MATRIX_MULTIPLICATION"

        # =============== DYNAMIC PROGRAMMING ===============
        if self._is_tsp_dp():
            return "TSP_DP"
        
        if self._is_subset_sum():
            return "SUBSET_SUM"

        # =============== COMBINATORIAL ===============
        if self._is_permutation():
            return "PERMUTATION"

        # =============== ARRAY ALGORITHMS ===============
        if self._is_kadane():
            return "KADANE"
        
        if self._is_frequency_count():
            return "FREQUENCY_COUNT"
        
        if self._is_find_max_min():
            return "FIND_MAX_MIN"
        
        if self._is_constant_time():
            return "CONSTANT_TIME"

        # =============== RECURSION FALLBACKS ===============
        if self._is_exponential_recursion():
            return "EXPONENTIAL_RECURSION"

        if self._is_linear_recursion():
            return "LINEAR_RECURSION"

        return None

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
                and "integer.max_value" in self.code or "int_max" in self.code or "inf" in self.code
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
        return (
            self.static.get("hasRecursion", False)
            and re.search(r"visited|seen", self.code)
            and re.search(r"adj|graph|neighbor", self.code)
        )

    def _is_graph_traversal(self) -> bool:
        """Generic graph traversal (BFS/DFS)."""
        return (
            re.search(r"graph|adj", self.code)
            and re.search(r"visited|seen", self.code)
        )

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
            self.static.get("maxLoopDepth", 0) == 2
            and re.search(r"min_idx|min_index|minidx", self.code)
            and re.search(r"swap|temp", self.code)
        )

    def _is_bubble_sort(self) -> bool:
        """Adjacent element comparison and swap."""
        return (
            self.static.get("maxLoopDepth", 0) == 2
            and re.search(r"bubble|swapped", self.code)
            and re.search(r"swap|temp", self.code)
        )

    def _is_quadratic_sort(self) -> bool:
        """Generic O(n²) sorting pattern."""
        return (
            self.static.get("maxLoopDepth", 0) == 2
            and re.search(r"swap|temp", self.code)
            and re.search(r"arr|list|array", self.code)
        )

    # ================== SEARCH ALGORITHMS ==================

    def _is_binary_search(self) -> bool:
        """Binary search with left/right/mid pointers."""
        return (
            re.search(r"mid", self.code)
            and (re.search(r"left|low|lo|start", self.code))
            and (re.search(r"right|high|hi|end", self.code))
            and (re.search(r"while|<=|>=", self.code) or self.static.get("hasRecursion", False))
        )

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
        return (
            self.static.get("maxLoopDepth", 0) >= 3
            and re.search(r"matrix|matri", self.code)
            or (
                self.static.get("maxLoopDepth", 0) >= 3
                and re.search(r"\[\s*\w+\s*\]\s*\[\s*\w+\s*\]", self.code)
                and re.search(r"\+=", self.code)
            )
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
        return self.static.get("hasRecursion", False)
