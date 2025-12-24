"""
🎯 Per-Function Complexity Analyzer
===================================
CORRECT approach to complexity analysis:

1. Split analysis into FUNCTION SCOPES
2. Compute complexity per-function independently
3. Classify recursion types correctly
4. Use MAX (not multiply) for worst-case
5. Never show single "overall" - show breakdown

Based on industry-correct definitions.
"""

import ast
import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from analyzer.std_lib_kb import METHOD_COMPLEXITY_MAP

class RecursionType(Enum):
    """Correct recursion classification patterns"""
    NONE = "none"
    LINEAR = "linear"           # f(n-1) → O(n)
    BINARY = "binary"           # f(n/2) → O(log n)
    DIVIDE_CONQUER = "divide_conquer"  # f(n/2) + f(n/2) + O(n) → O(n log n)
    EXPONENTIAL = "exponential"  # f(n-1) + f(n-2) → O(2^n)
    FACTORIAL = "factorial"      # permutation swap recursion → O(n!)


@dataclass
class FunctionComplexity:
    """Complexity analysis result for a single function"""
    name: str
    line_start: int
    line_end: int
    time_complexity: str
    space_complexity: str
    loop_depth: int = 0
    recursion_type: RecursionType = RecursionType.NONE
    recursion_calls: int = 0
    has_loop_in_recursion: bool = False
    data_structures: List[str] = field(default_factory=list)
    reasoning: str = ""
    category: str = "General"
    external_calls: List[Tuple[str, bool, str]] = field(default_factory=list)  # (name, is_constant_call, args_str)
    uses_param_as_bound: bool = False
    code: str = "" # Full code of the function for second-pass analysis


@dataclass
class AnalysisResult:
    """Complete analysis result with per-function breakdown"""
    functions: List[FunctionComplexity]
    worst_time: str
    worst_space: str
    worst_time_function: str
    worst_space_function: str
    complexity_level: str  # Low, Medium, High, Very High
    summary: str


class PerFunctionAnalyzer:
    """
    Analyzes code on a PER-FUNCTION basis.
    Never mixes functions. Never multiplies complexities.
    """
    
    COMPLEXITY_ORDER = {
        "O(1)": 0,
        "O(log n)": 1,
        "O(√n)": 2,
        "O(n)": 3,
        "O(V + E)": 3,
        "O(n log n)": 4,
        "O(E log V)": 4,
        "O(n²)": 5,
        "O(V²)": 5,
        "O(n³)": 6,
        "O(2ⁿ)": 7,
        "O(n!)": 8,
    }
    
    def __init__(self, code: str):
        self.code = code
        self.functions: List[FunctionComplexity] = []
    
    def analyze(self) -> AnalysisResult:
        """Main analysis - split by function, analyze each, return worst-case."""
        
        # Try Python AST first
        try:
            tree = ast.parse(self.code)
            self._analyze_python_ast(tree)
        except SyntaxError:
            # Fallback for other languages
            self._analyze_generic()
        
        # If no functions found, analyze as single block
        if not self.functions:
            self.functions.append(self._analyze_code_block(
                "main", self.code, 1, len(self.code.split('\n'))
            ))
        
        # Phase 2: Global Effective Complexity Analysis
        # Track which variables are literals (constant sources)
        literal_vars = set()
        for f in self.functions:
            # Simple heuristic for literal assignment in 'main'
            assigns = re.findall(r'\b(?:int|let|const|var|static\s+int)\s+([a-zA-Z_]\w*)\s*=\s*[\d"\'truefalsenull]+', f.code)
            for v in assigns: literal_vars.add(v)

        called_with_scaling = set()
        for f in self.functions:
            for name, is_const, args in f.external_calls:
                # A call is scaling ONLY if args contains a variable NOT in literal_vars
                actual_scaling = not is_const
                if not is_const and args:
                    # check if the variables in args are all literals/constant-sourced
                    arg_vars = re.findall(r'\b([a-zA-Z_]\w*)\b', args)
                    if arg_vars and all(v in literal_vars for v in arg_vars):
                        actual_scaling = False
                
                if actual_scaling:
                    called_with_scaling.add(name)
        
        # Compute Intrinsic Worst Case (Structural potential)
        intrinsic_times = [f.time_complexity for f in self.functions]
        intrinsic_worst_time = self._get_worst_complexity(intrinsic_times)
        
        effective_times = []
        for f in self.functions:
            is_entry = f.name == "main" or f.name.startswith("run_")
            is_scaling = f.name in called_with_scaling or f.uses_param_as_bound
            
            # COLLAPSE RULE: Demo code called with constants is O(1) effectively
            should_collapse = False
            if f.time_complexity in ["O(2ⁿ)", "O(n!)", "O(n³)", "O(n²)"]:
                if not is_scaling and not is_entry:
                    should_collapse = True
            
            if should_collapse:
                effective_times.append((f.name, "O(1)"))
            else:
                effective_times.append((f.name, f.time_complexity))

        # Compute program-level effective worst case
        effective_worst_time = self._get_worst_complexity([et[1] for et in effective_times])
        
        # DUAL-MODE RESOLUTION:
        # If the code snippet is small (likely a demo) or contains high-complexity algorithms,
        # prioritize the INTRINSIC theoretical complexity over the EFFECTIVE runtime complexity.
        # This prevents 'fib(5)' from being reported as O(1) when the user wants to know about 'fib(n)'.
        is_high_complexity = intrinsic_worst_time in ["O(2ⁿ)", "O(n!)", "O(n³)", "O(n²)"]
        is_short_code = len(self.code.split('\n')) < 50
        
        if intrinsic_worst_time in ["O(2ⁿ)", "O(n!)", "O(n³)", "O(n²)"] or is_short_code:
             print(f"DEBUG: Forcing Intrinsic Complexity {intrinsic_worst_time} (Effective was {effective_worst_time})")
             worst_time = intrinsic_worst_time
             is_collapsed_demo = False
        else:
            worst_time = effective_worst_time
            is_collapsed_demo = True

        # RULE 3: Global Space Analysis
        # Check for global arrays that might dominate space (e.g. adj[100][100])
        global_space = []
        global_code = self.code
        # Remove function bodies to see only global scope roughly (heuristic)
        # (This is tricky with regex, but we look for top-level array decls)
        array_matches = re.finditer(r'(?:int|float|double|bool|char|long)\s+(\w+)\s*\[([^\]]*)\](?:\s*\[([^\]]*)\])?', global_code)
        for m in array_matches:
            dim1 = m.group(2)
            dim2 = m.group(3)
            if dim2: # 2D array
                if re.search(r'\b(n|v|e)\b', dim1.lower()) or re.search(r'\b(n|v|e)\b', dim2.lower()):
                    global_space.append("O(n²)") # Or V^2, genericized to n^2 internally then mapped
                else: 
                     # Check if it looks large constant
                    try:
                         if int(dim1) * int(dim2) > 1000: global_space.append("O(1)") # Large constant block
                    except: pass
            elif dim1:
                if re.search(r'\b(n|v|e)\b', dim1.lower()):
                    global_space.append("O(n)")

        effective_spaces = []
        for f in self.functions:
            effective_spaces.append((f.name, f.space_complexity))
        
        # Add global space to consideration
        for gs in global_space:
             effective_spaces.append(("global_memory", gs))

        worst_space = self._get_worst_complexity([es[1] for es in effective_spaces])
        
        # Consistent Driver Attribution
        worst_time_funcs = [f.name for f in self.functions if f.time_complexity == worst_time]
        if len(worst_time_funcs) > 1 and "main" in worst_time_funcs:
            worst_time_funcs.remove("main")
            
        worst_space_funcs = [es[0] for es in effective_spaces if es[1] == worst_space]
        if len(worst_space_funcs) > 1 and "main" in worst_space_funcs:
            worst_space_funcs.remove("main")
        
        # Fallback if everything is O(1)
        if not worst_time_funcs: worst_time_funcs = [et[0] for et in effective_times if et[1] == worst_time]
        if not worst_space_funcs: worst_space_funcs = [es[0] for es in effective_spaces if es[1] == worst_space]

        worst_time_func_str = ", ".join(worst_time_funcs)
        worst_space_func_str = ", ".join(worst_space_funcs)
        
        # Determine complexity level
        level = self._get_complexity_level(worst_time)
        
        # Generate summary
        summary = self._generate_summary(worst_time, worst_space, worst_time_funcs)
        
        return AnalysisResult(
            functions=self.functions,
            worst_time=worst_time,
            worst_space=worst_space,
            worst_time_function=worst_time_func_str,
            worst_space_function=worst_space_func_str,
            complexity_level=level,
            summary=summary
        )
    
    def _analyze_python_ast(self, tree: ast.AST):
        """Analyze Python code using AST - per function."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function code using line numbers (compatible with all Python versions)
                lines = self.code.split('\n')
                end_line = getattr(node, 'end_lineno', node.lineno + 10)
                func_code = '\n'.join(lines[node.lineno-1:end_line])
                
                func_analysis = self._analyze_python_function(node, func_code)
                self.functions.append(func_analysis)
    
    def _analyze_python_function(self, node: ast.FunctionDef, func_code: str) -> FunctionComplexity:
        """Analyze a single Python function using TAINT ANALYSIS."""
        
        # Count loops and track depth
        loop_depth = 0
        max_loop_depth = 0
        loop_count = 0
        
        # Track recursion
        recursion_calls = 0
        func_name = node.name
        
        # Track data structures for space
        data_structures = []
        
        # ==========================================
        # TAINT TRACKING SYSTEM
        # ==========================================
        tainted_vars: Set[str] = set()
        
        # 1. Initialize Taint: Arguments are sources of scaling
        for arg in node.args.args:
            tainted_vars.add(arg.arg)
            
        class TaintVisitor(ast.NodeVisitor):
            def __init__(self):
                self.loop_depth = 0
                self.max_loop_depth = 0
                self.loop_count = 0
                self.has_loop_in_recursion = False
                self.allocations = []
                self.external_calls = []
                self.params = [a.arg for a in node.args.args]
                self.uses_param_as_bound = False # Does any loop depend on contaminated vars?
                self.recursion_calls = 0
                self.in_recursion = False
                
                # Complexity Accumulators
                self.detected_complexities = [] # Stores e.g. ["O(n)", "O(log n)"] from API calls
                
            def is_node_tainted(self, n) -> bool:
                """Check if an AST node involves a tainted variable."""
                for name_node in ast.walk(n):
                    if isinstance(name_node, ast.Name) and name_node.id in tainted_vars:
                        return True
                return False
                
            def visit_Assign(self, n):
                """Propagate taint: x = n * 2 (x becomes tainted)"""
                # Check if RHS is tainted
                rhs_tainted = self.is_node_tainted(n.value)
                
                # Check if RHS is a scaling function call (e.g. x = range(n))
                if isinstance(n.value, ast.Call):
                    # Check method map
                    func_id = None
                    if isinstance(n.value.func, ast.Name): func_id = n.value.func.id
                    elif isinstance(n.value.func, ast.Attribute): func_id = n.value.func.attr
                    
                    if func_id in METHOD_COMPLEXITY_MAP:
                        # If a function returns a large structure (e.g. list), the result is tainted structure
                        # But here we mainly care about SCALAR taint (scaling numbers)
                        # Assume complexity map ops don't return scaling SCALARS usually, except 'len' (which passes taint)
                        if func_id == 'len':
                            rhs_tainted = self.is_node_tainted(n.value)

                # Assign taint to LHS
                if rhs_tainted:
                    for target in n.targets:
                        if isinstance(target, ast.Name):
                            tainted_vars.add(target.id)
                else:
                    # Sanitize: x = 5 (x is no longer tainted)
                    for target in n.targets:
                        if isinstance(target, ast.Name) and isinstance(n.value, (ast.Constant, ast.Num, ast.Str)):
                            if target.id in tainted_vars:
                                tainted_vars.remove(target.id)
                self.generic_visit(n)

            def visit_For(self, n):
                self.loop_count += 1
                self.loop_depth += 1
                self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
                
                if self.in_recursion:
                    self.has_loop_in_recursion = True
                
                # TAINT CHECK: Loop bound
                is_tainted_bound = False
                if hasattr(n, 'iter'):
                     is_tainted_bound = self.is_node_tainted(n.iter)
                
                if is_tainted_bound:
                    self.uses_param_as_bound = True
                
                self.generic_visit(n)
                self.loop_depth -= 1
            
            def visit_While(self, n):
                self.loop_count += 1
                self.loop_depth += 1
                self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
                
                if self.in_recursion:
                    self.has_loop_in_recursion = True
                
                # TAINT CHECK: Loop condition
                if self.is_node_tainted(n.test):
                    self.uses_param_as_bound = True
                        
                self.generic_visit(n)
                self.loop_depth -= 1
            
            def visit_Call(self, n):
                func_id = None
                if isinstance(n.func, ast.Name):
                    func_id = n.func.id
                elif isinstance(n.func, ast.Attribute):
                    func_id = n.func.attr
                
                # Recursion Check
                if func_id == func_name:
                    self.recursion_calls += 1
                    self.in_recursion = True
                    # Check taint in arguments
                    if any(self.is_node_tainted(arg) for arg in n.args):
                        self.uses_param_as_bound = True
                else:
                    # Standard Lib Complexity Check
                    if func_id in METHOD_COMPLEXITY_MAP:
                        # Only count complexity if arguments are tainted!
                        # e.g. sort([1,2,3]) is O(1). sort(input_arr) is O(N log N).
                        args_tainted = any(self.is_node_tainted(arg) for arg in n.args)
                        
                        # Special case: 'append' / 'add' on a TAINTED list is O(1) usually, but O(N) amortized
                        # We use the map.
                        if args_tainted or isinstance(n.func, ast.Attribute) and (isinstance(n.func.value, ast.Name) and n.func.value.id in tainted_vars):
                             complexity = METHOD_COMPLEXITY_MAP[func_id]
                             if complexity != "O(1)":
                                 self.detected_complexities.append(complexity)

                    # External Call Tracker
                    args_str = ", ".join([ast.dump(arg) for arg in n.args])
                    is_constant = len(n.args) > 0 and all(isinstance(arg, (ast.Constant, ast.Num, ast.Str, ast.Bytes, ast.NameConstant)) for arg in n.args)
                    self.external_calls.append((func_id or "unknown", is_constant, args_str))
                    
                self.generic_visit(n)
            
            def visit_List(self, n):
                self.allocations.append("list")
                # List construction with tainted vars is O(N) copy check?
                # Usually list literal [a,b,c] is O(1) unless unpacked
                self.generic_visit(n)
            
            def visit_Dict(self, n):
                self.allocations.append("dict")
                self.generic_visit(n)
            
            def visit_ListComp(self, n):
                self.allocations.append("list_comp")
                # List comp is implicit loop
                for gen in n.generators:
                    if self.is_node_tainted(gen.iter):
                        self.uses_param_as_bound = True
                        self.detected_complexities.append("O(n)")
                self.generic_visit(n)
        
        visitor = TaintVisitor()
        visitor.visit(node)
        
        loop_depth = visitor.max_loop_depth
        loop_count = visitor.loop_count
        recursion_calls = visitor.recursion_calls
        data_structures = visitor.allocations
        
        # Classify recursion type CORRECTLY
        recursion_type = self._classify_recursion(
            func_code, func_name, recursion_calls, 
            visitor.has_loop_in_recursion, loop_depth
        )
        
        # Compute time complexity based on Taint Analysis & Loops
        # 1. Base Structural Complexity (Loops)
        base_time = self._compute_time_complexity(
            loop_depth, loop_count, recursion_type, 
            recursion_calls, visitor.has_loop_in_recursion, func_code
        )
        
        # 2. API / Library Complexity check
        api_time = self._get_worst_complexity(visitor.detected_complexities) if visitor.detected_complexities else "O(1)"
        
        # 3. Combine
        final_time = self._get_worst_complexity([base_time, api_time])
        
        # 4. IF Taint Analysis says 'Constant', downgrade?
        # Only downgrade if loops > 0 OR recursion > 0.
        # If Visitor says 'uses_param_as_bound' is False, and API calls are clean...
        # strict check:
        if (loop_count > 0 or recursion_calls > 0) and not visitor.uses_param_as_bound:
            # Code has loops, but they don't depend on inputs. O(1).
            # e.g. for i in range(100): print(i)
            # CAUTION: 'calls' might have side effects? Assuming pure algorithmic analysis.
            if not visitor.detected_complexities:
                 final_time = "O(1)"

        # Compute space complexity
        space_complexity = self._compute_space_complexity(
            data_structures, recursion_type, loop_depth, func_code
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            loop_depth, recursion_type, recursion_calls, final_time, func_code
        )
        
        if not visitor.uses_param_as_bound and (loop_count > 0 or recursion_calls > 0):
            reasoning += " (Loops/Recursion operate on constant bounds)."
        
        return FunctionComplexity(
            name=func_name,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno + 10),
            time_complexity=final_time,
            space_complexity=space_complexity,
            loop_depth=loop_depth,
            recursion_type=recursion_type,
            recursion_calls=recursion_calls,
            has_loop_in_recursion=visitor.has_loop_in_recursion,
            data_structures=data_structures,
            reasoning=reasoning,
            external_calls=visitor.external_calls,
            uses_param_as_bound=visitor.uses_param_as_bound,
            code=func_code
        )
    
    def _classify_recursion(self, code: str, func_name: str, 
                           recursion_calls: int, has_loop: bool, 
                           loop_depth: int) -> RecursionType:
        """
        CORRECT recursion classification based on patterns:
        - f(n-1) → O(n) LINEAR
        - f(n/2) → O(log n) BINARY
        - f(n/2) + f(n/2) + merge → O(n log n) DIVIDE_CONQUER
        - f(n-1) + f(n-2) → O(2^n) EXPONENTIAL
        - permutation swap recursion → O(n!) FACTORIAL
        """
        if recursion_calls == 0:
            return RecursionType.NONE
        
        code_lower = code.lower()
        
        # 1. GRAPH TRAVERSAL vs FACTORIAL check
        if recursion_calls >= 1 and has_loop:
            is_graph = any(w in code_lower for w in ["visited", "seen", "adj", "neighbor", "edge", "graph", "marked", "is_visited"])
            has_backtrack = any(w in code_lower for w in ["remove", "pop", "undo"]) or ("visited[" in code_lower and any(v in code_lower for v in ["false", "null", "0", "none"]))
            
            # Graph traversals like DFS/BFS are O(V+E), not factorial
            if is_graph and not has_backtrack:
                return RecursionType.LINEAR # DFS search space is linear in V+E
            
            if re.search(r'for\s+\w+\s+in\s+range|for\s*\(.*;\s*.*;\s*.*\)|for\s*\(.*\s*:\s*.*\)', code_lower):
                return RecursionType.FACTORIAL
        
        # 2. EXPONENTIAL pattern: multiple recursive calls NOT inside a loop
        if recursion_calls >= 2:
            # Look for bifurcating calls: f(n-1) and f(n-2) or multiple calls to self
            matches = re.findall(rf'{re.escape(func_name)}\s*\(', code)
            if len(matches) >= 2:
                # f(n-1) + f(n-2) pattern
                if re.search(rf'{re.escape(func_name)}.*-\s*1.*{re.escape(func_name)}.*-\s*2', code, re.DOTALL):
                    return RecursionType.EXPONENTIAL
                # General branching factor (not in loop)
                if not re.search(r'/\s*2|//\s*2|>>\s*1|mid|left|right', code_lower):
                    return RecursionType.EXPONENTIAL
        
        # 3. DIVIDE_CONQUER pattern
        if (re.search(r'/\s*2|//\s*2|>>\s*1', code) or re.search(r'mid|pivot|partition', code_lower)):
            if recursion_calls >= 2:
                # Check for QuickSort (usually has 'partition' or 'pivot')
                if re.search(r'partition|pivot', code_lower):
                    # We classify this as a special type that defaults to O(n²) worst case
                    return RecursionType.DIVIDE_CONQUER
            return RecursionType.DIVIDE_CONQUER
        
        # 4. BINARY pattern (Binary Search / f(n/2))
        # f(n/2)
        if (re.search(r'/\s*2|//\s*2|>>\s*1', code) or 
            re.search(rf'{func_name}\s*\([^)]*/\s*2[^)]*\)', code)):
            return RecursionType.BINARY
        
        # 5. LINEAR pattern (f(n-1))
        # f(n-1)
        if re.search(rf'{func_name}\s*\([^)]*-\s*1[^)]*\)', code):
            return RecursionType.LINEAR
        
        # Default fallback
        return RecursionType.LINEAR
    
    def _compute_time_complexity(self, loop_depth: int, loop_count: int,
                                 recursion_type: RecursionType, 
                                 recursion_calls: int,
                                 has_loop_in_recursion: bool,
                                 code: str) -> str:
        """Compute time complexity from analyzed metrics."""
        
        # First check recursion type (higher priority)
        if recursion_type == RecursionType.FACTORIAL:
            return "O(n!)"
        
        if recursion_type == RecursionType.EXPONENTIAL:
            return "O(2ⁿ)"
        
        if recursion_type == RecursionType.DIVIDE_CONQUER:
            # Worst-case for QuickSort is O(n²), for MergeSort O(n log n). 
            # If we see pivot/partition, assume O(n²) worst-case.
            if re.search(r'partition|pivot', code.lower()):
                return "O(n²)"
            return "O(n log n)"
        
        if recursion_type == RecursionType.BINARY:
            return "O(log n)"
        
        if recursion_type == RecursionType.LINEAR:
            if has_loop_in_recursion:
                return "O(n²)"  # Linear recursion with loop inside
            return "O(n)"
        
        # No recursion - check loops
        if loop_depth == 0:
            return "O(1)"
        
        if loop_depth == 1:
            # 1. Logarithmic check (Binary Search / Divide)
            log_patterns = [
                r'\*=\s*2', r'/=\s*2', r'//=\s*2', r'>>=\s*1', 
                r'low\s*=\s*mid\s*\+\s*1', r'high\s*=\s*mid\s*-\s*1',
                r'left\s*=\s*mid\s*\+\s*1', r'right\s*=\s*mid\s*-\s*1',
                r'start\s*=\s*mid\s*\+\s*1', r'end\s*=\s*mid\s*-\s*1'
            ]
            if any(re.search(p, code) for p in log_patterns):
                return "O(log n)"
            
            # 2. Square root loop
            if re.search(r'sqrt\s*\(|i\s*\*\s*i\s*<=|i\s*\*\s*i\s*<', code):
                return "O(√n)"
            
            return "O(n)"
        
        if loop_depth == 2:
            return "O(n²)"
        
        if loop_depth == 3:
            return "O(n³)"
        
        return f"O(n^{loop_depth})"
    
    def _compute_space_complexity(self, data_structures: List[str],
                                  recursion_type: RecursionType,
                                  loop_depth: int, code: str) -> str:
        """
        Compute space complexity based on:
        - Data structure allocations
        - Recursion stack depth
        - NOT summing, using MAX
        """
        space_complexities = []
        
        # Check for 2D array/matrix ALLOCATION (not just mention)
        if re.search(r'new\s+\w+\[[^\]]+\]\s*\[|\[\w+\]\s*\[\w+\]\s*=|\[\s*\[.*for.*in.*\]', code):
            space_complexities.append("O(n²)")
        elif re.search(r'matrix|grid|table', code.lower()) and "[" in code:
            # Softer check for matrix usage
            space_complexities.append("O(n²)")
        
        # Check for DP table (Scaling)
        if re.search(r'dp\s*\[|memo\s*\[', code.lower()):
            if re.search(r'\]\s*\[', code):  # 2D table
                space_complexities.append("O(n²)")
            else:
                space_complexities.append("O(n)")
        
        # Check for list/array allocation in loop
        if data_structures and loop_depth > 0:
            space_complexities.append("O(n)")
        elif data_structures:
            space_complexities.append("O(n)")
        
        # Recursion stack space
        if recursion_type == RecursionType.BINARY:
            space_complexities.append("O(log n)")
        elif recursion_type == RecursionType.DIVIDE_CONQUER:
            # Merge sort uses O(n) temp array. Quick sort is O(log n) stack.
            if "partition" in code.lower() or "pivot" in code.lower():
                space_complexities.append("O(log n)") # QuickSort stack
            else:
                space_complexities.append("O(n)") # MergeSort temp array
        elif recursion_type in [RecursionType.LINEAR, RecursionType.EXPONENTIAL]:
            space_complexities.append("O(n)")
        elif recursion_type == RecursionType.FACTORIAL:
            space_complexities.append("O(n)")
        
        if not space_complexities:
            return "O(1)"
        
        # Return MAX (not sum!)
        return self._get_worst_complexity(space_complexities)
    
    def _generate_reasoning(self, loop_depth: int, 
                           recursion_type: RecursionType,
                           recursion_calls: int, 
                           time_complexity: str,
                           code: str) -> str:
        """Generate human-readable reasoning."""
        reasons = []
        
        if loop_depth > 0:
            reasons.append(f"{loop_depth} nested loop(s)")
        
        if recursion_type != RecursionType.NONE:
            type_desc = {
                RecursionType.LINEAR: "linear recursion",
                RecursionType.BINARY: "logarithmic recursion f(n/2)",
                RecursionType.DIVIDE_CONQUER: "divide & conquer branching",
                RecursionType.EXPONENTIAL: "exponential doubling f(n-1)+f(n-2)",
                RecursionType.FACTORIAL: "factorial branching (backtracking)"
            }
            reasons.append(type_desc.get(recursion_type, str(recursion_type.value)))
        
        # Add Graph context if detected
        if any(w in (reasons[-1].lower() if reasons else "") for w in ["linear", "nested"]) and "visited" in code.lower():
            reasons.append("graph traversal structure O(V+E)")
        
        if not reasons:
            reasons.append("constant-time operations")
        
        return f"{time_complexity} because: {', '.join(reasons)}"
    
    def _analyze_generic(self):
        """Analyze non-Python code by detecting function boundaries."""
        # Pattern for function definitions (improved for Java/C++ modifiers)
        # Capture: 1. modifiers, 2. return type, 3. function name, 4. parameter list
        func_pattern = r'(?:public|private|protected|static|final|synchronized|volatile|native|abstract|void|int|bool|string|double|float|auto|function|def|[\w<>\b\[\]]+)\s+([\w\d_]+)\s*\(([^)]*)\)\s*(?:throws\s+[\w\s,]+)?\s*\{'
        
        lines = self.code.split('\n')
        current_func = None
        current_params = []
        func_start = 0
        brace_depth = 0
        func_body_lines = []
        
        for i, line in enumerate(lines, 1):
            match = re.search(func_pattern, line)
            
            if match and brace_depth == 0:
                current_func = match.group(1)
                # Parse params (crude split but effective for common types)
                params_str = match.group(2)
                current_params = [p.strip().split()[-1] for p in params_str.split(',') if p.strip()]
                # remove any leading * or & for C++
                current_params = [p.lstrip('*&') for p in current_params]
                
                func_start = i
                brace_depth = line.count('{') - line.count('}')
                func_body_lines = [line]
            elif current_func:
                func_body_lines.append(line)
                brace_depth += line.count('{') - line.count('}')
                
                if brace_depth <= 0:
                    # End of function
                    func_code = '\n'.join(func_body_lines)
                    analysis = self._analyze_code_block(
                        current_func, func_code, func_start, i, current_params
                    )
                    self.functions.append(analysis)
                    current_func = None
                    func_body_lines = []
    
    def _analyze_code_block(self, name: str, code: str, 
                           line_start: int, line_end: int, params: List[str] = None) -> FunctionComplexity:
        """Analyze a generic code block."""
        params = params or []
        name_lower = name.lower()
        code_lower = code.lower()
        
        # Determine category based on name
        category = "General"
        if any(w in name_lower for w in ["sort", "partition", "heapify", "swap"]):
            category = "Sorting"
        elif any(w in name_lower for w in ["search", "find", "binary"]):
            category = "Searching"
        elif any(w in name_lower for w in ["matrix", "multiply", "grid", "flood", "matrix"]):
            category = "Matrix"
        elif any(w in name_lower for w in ["fib", "fact", "recursive", "permute", "combination"]):
            category = "Math/Recursion"
        elif any(w in name_lower for w in ["dp", "lcs", "knapsack", "edit", "subsequence"]):
            category = "Dynamic Programming"
        elif any(w in name_lower for w in ["graph", "bfs", "dfs", "tree", "node", "topo", "dijkstra"]):
            category = "Graph"
        elif any(w in name_lower for w in ["queen", "sudoku", "solve", "path"]):
            category = "Backtracking"

        # Estimate loop depth using brace tracking
        loop_depth = self._estimate_loop_depth(code)

        # Detect composite DS operations (O(1) average)
        if any(w in code for w in ["Set", "Map", "unordered_map", "unordered_set", "HashMap", "HashSet", "dict", "set()"]):
            if re.search(r'\.(has|get|add|set|put|contains|find|insert)\b', code):
                if loop_depth <= 1: 
                    pass

        # Count loops
        loop_matches = list(re.finditer(r'\b(for|while)\s*\(', code))
        loop_count = len(loop_matches)
        
        # Detect all external calls in the block and identify constant vs scaling
        external_calls = []
        determined_recursion_calls = 0
        
        call_matches = re.finditer(r'\b([a-zA-Z_]\w*)\s*\(([^)]*)\)', code)
        for m in call_matches:
            c_name = m.group(1)
            args_str = m.group(2).strip()
            
            if c_name == name: 
                determined_recursion_calls += 1
                continue # skip adding to external_calls list
            
            # Constant if empty or only literals/digits (e.g. 8, 20, "ABC")
            # If it contains a word that looks like a variable (n, size, len) -> scaling
            is_const = True
            if args_str:
                if re.search(r'\b(n|m|k|size|len|arr|args)\b', args_str.lower()):
                    is_const = False
                elif not re.match(r'^[\d\s,."\'\-truefalsenull]+$', args_str.lower()):
                    is_const = False
            external_calls.append((c_name, is_const, args_str))

        # Detect recursion (self-calls)
        recursion_calls = determined_recursion_calls
        
        # Check for loop in recursion context
        has_loop_in_recursion = recursion_calls > 0 and loop_count > 0
        
        # Classify recursion
        recursion_type = self._classify_recursion(
            code, name, recursion_calls, has_loop_in_recursion, loop_depth
        )
        
        # Compute complexities
        time_complexity = self._compute_time_complexity(
            loop_depth, loop_count, recursion_type, 
            recursion_calls, has_loop_in_recursion, code
        )
        
        space_complexity = self._compute_space_complexity(
            [], recursion_type, loop_depth, code
        )
        
        # Check if param used as bound in non-python
        uses_param_as_bound = False
        for param in params:
            # Check for param in for loop condition or while loop
            if re.search(rf'for\s*\([^;]*;\s*[^;]*{re.escape(param)}|while\s*\([^)]*{re.escape(param)}', code):
                uses_param_as_bound = True
                break
            # Check for param in recursive call decrement/driver
            if recursion_calls > 0:
                if re.search(rf'{re.escape(name)}\s*\([^)]*{re.escape(param)}', code[len(name)+5:]):
                    uses_param_as_bound = True
                    break

        # CATEGORY OVERRIDE for Tree/Graph (O(V+E) or O(log n))
        if category == "Graph" and time_complexity == "O(n²)":
            time_complexity = "O(V + E)"
        elif category == "Graph" and time_complexity == "O(n³)":
            time_complexity = "O(V³)"
        elif category == "Searching" and "binary" in name_lower:
            time_complexity = "O(log n)"
        elif category == "Searching" and ("search" in name_lower or "find" in name_lower) and "tree" in code_lower:
            time_complexity = "O(log n)" # BST average search

        reasoning = self._generate_reasoning(
            loop_depth, recursion_type, recursion_calls, time_complexity, code
        )
        
        return FunctionComplexity(
            name=name,
            line_start=line_start,
            line_end=line_end,
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            loop_depth=loop_depth,
            recursion_type=recursion_type,
            recursion_calls=recursion_calls,
            has_loop_in_recursion=has_loop_in_recursion,
            reasoning=reasoning,
            category=category,
            external_calls=external_calls,
            uses_param_as_bound=uses_param_as_bound,
            code=code
        )
    
    
    def _is_interactive_loop(self, line: str) -> bool:
        """Rule 7: Interactive loops (menus, servers) do not scale."""
        if re.search(r'while\s*\(\s*(true|1|TRUE)\s*\)', line): return True
        if re.search(r'for\s*\(\s*;\s*;\s*\)', line): return True
        if re.search(r'while\s*\(\s*.*\b(input|scanf|cin|next|read)\b', line.lower()): return True
        return False

    def _estimate_loop_depth(self, code: str) -> int:
        """
        Estimate maximum nested loop depth with multi-language resilience.
        Specially handles C-style code where innermost loops might omit braces.
        """
        max_depth = 0
        current_depth = 0
        loop_starts = []
        brace_depth = 0
        
        for line in code.split('\n'):
            line = line.strip()
            # Loop keyword detection
            if re.search(r'\b(for|while)\s*\(', line):
                # RULE 7 Check: If loop is interactive/infinite, do not count as scaling logic
                if not self._is_interactive_loop(line):
                    current_depth += 1
                    max_depth = max(max_depth, current_depth)
                    loop_starts.append(brace_depth)
            
            # Braces detection
            brace_depth += line.count('{') - line.count('}')
            
            # UN-NESTING LOGIC:
            while loop_starts and brace_depth < loop_starts[-1]:
                loop_starts.pop()
                current_depth -= 1
        
        return max_depth

    def _get_worst_complexity(self, complexities: List[str]) -> str:
        """Return the WORST (highest) complexity using MAX, not multiply."""
        if not complexities:
            return "O(1)"
        
        return max(complexities, key=lambda c: self.COMPLEXITY_ORDER.get(c, 0))
    
    def _get_complexity_level(self, worst_time: str) -> str:
        """Get human-readable complexity level."""
        order = self.COMPLEXITY_ORDER.get(worst_time, 0)
        
        if order <= 1:
            return "Low"
        elif order <= 4:
            return "Medium"
        elif order <= 6:
            return "High"
        else:
            return "Very High"
    
    def _generate_summary(self, worst_time: str, worst_space: str, 
                         worst_funcs: List[str]) -> str:
        """Generate analysis summary."""
        num_funcs = len(self.functions)
        categories = list(set(f.category for f in self.functions if f.category != "General"))
        
        return f"Deterministic Analysis: {worst_time} time, {worst_space} space."


def analyze_per_function(code: str) -> dict:
    """Helper for internal usage."""
    analyzer = PerFunctionAnalyzer(code)
    result = analyzer.analyze()
    return {
        "functions": [
            {
                "name": f.name,
                "timeComplexity": f.time_complexity,
                "spaceComplexity": f.space_complexity,
                "reasoning": f.reasoning,
                "complexity": f.time_complexity # Legacy compat
            } for f in result.functions
        ],
        "worstTime": result.worst_time,
        "worstSpace": result.worst_space,
        "worstTimeFunction": result.worst_time_function,
        "worstSpaceFunction": result.worst_space_function,
        "summary": result.summary
    }
