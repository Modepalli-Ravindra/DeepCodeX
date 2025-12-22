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
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


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
    external_calls: List[Tuple[str, bool]] = field(default_factory=list)  # (name, is_constant_call)
    uses_param_as_bound: bool = False


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
        called_with_scaling = set()
        for f in self.functions:
            for name, is_const in f.external_calls:
                if not is_const:
                    called_with_scaling.add(name)
        
        # Compute worst-case among INTRINSIC complexities
        intrinsic_times = [f.time_complexity for f in self.functions]
        intrinsic_worst_time = self._get_worst_complexity(intrinsic_times)
        
        effective_times = []
        for f in self.functions:
            is_entry = f.name == "main" or f.name.startswith("run_")
            is_scaling = f.name in called_with_scaling
            
            should_collapse = False
            if f.time_complexity in ["O(2ⁿ)", "O(n!)", "O(n³)", "O(n²)"]:
                if not is_scaling and not is_entry and not f.uses_param_as_bound:
                    should_collapse = True
            
            if should_collapse:
                effective_times.append((f.name, "O(1)"))
            else:
                effective_times.append((f.name, f.time_complexity))

        # Compute worst-case among EFFECTIVE complexities
        effective_worst_time = self._get_worst_complexity([et[1] for et in effective_times])
        
        # DUAL-MODE LOGIC:
        # If effective is O(1) but intrinsic is higher, and it's a small demo file:
        # Prioritize showing the Intrinsic truth.
        if effective_worst_time == "O(1)" and intrinsic_worst_time != "O(1)":
            worst_time = intrinsic_worst_time
            is_collapsed_demo = True
        else:
            worst_time = effective_worst_time
            is_collapsed_demo = False

        effective_spaces = []
        for f in self.functions:
            effective_spaces.append((f.name, f.space_complexity))
                
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
        """Analyze a single Python function."""
        
        # Count loops and track depth
        loop_depth = 0
        max_loop_depth = 0
        loop_count = 0
        
        # Track recursion
        recursion_calls = 0
        func_name = node.name
        
        # Track data structures for space
        data_structures = []
        
        class FunctionVisitor(ast.NodeVisitor):
            def __init__(self):
                self.loop_depth = 0
                self.max_loop_depth = 0
                self.loop_count = 0
                self.has_loop_in_recursion = False
                self.allocations = []
                self.external_calls = []
                self.params = [a.arg for a in node.args.args]
                self.uses_param_as_bound = False
                self.recursion_calls = 0
                self.in_recursion = False
            
            def visit_For(self, n):
                self.loop_count += 1
                self.loop_depth += 1
                self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
                if self.in_recursion:
                    self.has_loop_in_recursion = True
                
                # Check if param is used in range() or iterator
                if hasattr(n, 'iter'):
                    for name_node in ast.walk(n.iter):
                        if isinstance(name_node, ast.Name) and name_node.id in self.params:
                            self.uses_param_as_bound = True
                
                self.generic_visit(n)
                self.loop_depth -= 1
            
            def visit_While(self, n):
                self.loop_count += 1
                self.loop_depth += 1
                self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
                if self.in_recursion:
                    self.has_loop_in_recursion = True
                
                # Check if param is used in test
                for name_node in ast.walk(n.test):
                    if isinstance(name_node, ast.Name) and name_node.id in self.params:
                        self.uses_param_as_bound = True
                        
                self.generic_visit(n)
                self.loop_depth -= 1
            
            def visit_Call(self, n):
                if isinstance(n.func, ast.Name):
                    if n.func.id == func_name:
                        self.recursion_calls += 1
                        self.in_recursion = True
                        
                        # Check if param is used in recursive call args (decrement/driver)
                        for arg in n.args:
                            for name_node in ast.walk(arg):
                                if isinstance(name_node, ast.Name) and name_node.id in self.params:
                                    self.uses_param_as_bound = True
                    else:
                        # Detect if call is constant-bounded (literal arguments)
                        is_constant = len(n.args) > 0 and all(isinstance(arg, (ast.Constant, ast.Num, ast.Str, ast.Bytes, ast.NameConstant)) for arg in n.args)
                        self.external_calls.append((n.func.id, is_constant))
                self.generic_visit(n)
            
            def visit_List(self, n):
                self.allocations.append("list")
                self.generic_visit(n)
            
            def visit_Dict(self, n):
                self.allocations.append("dict")
                self.generic_visit(n)
            
            def visit_ListComp(self, n):
                self.allocations.append("list_comp")
                self.generic_visit(n)
        
        visitor = FunctionVisitor()
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
        
        # Compute time complexity
        time_complexity = self._compute_time_complexity(
            loop_depth, loop_count, recursion_type, 
            recursion_calls, visitor.has_loop_in_recursion, func_code
        )
        
        # Compute space complexity
        space_complexity = self._compute_space_complexity(
            data_structures, recursion_type, loop_depth, func_code
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            loop_depth, recursion_type, recursion_calls, time_complexity, func_code
        )
        
        return FunctionComplexity(
            name=func_name,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno + 10),
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            loop_depth=loop_depth,
            recursion_type=recursion_type,
            recursion_calls=recursion_calls,
            has_loop_in_recursion=visitor.has_loop_in_recursion,
            data_structures=data_structures,
            reasoning=reasoning,
            external_calls=visitor.external_calls,
            uses_param_as_bound=visitor.uses_param_as_bound
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
        
        # 1. FACTORIAL pattern: recursive call INSIDE a loop (branching factor grows with n)
        if recursion_calls >= 1 and has_loop:
            # HEURISTIC: Graph Traversal check
            # If we see visited check or adj list, and NO backtracking (undoing state), it's just DFS.
            is_graph = any(w in code_lower for w in ["visited", "seen", "adj", "neighbor", "edge", "graph"])
            # Backtracking check: Look for removing/popping or resetting visited to false
            has_backtrack = any(w in code_lower for w in ["remove", "pop", "undo", "visited["] and ("false" in code_lower or "null" in code_lower or "0" in code_lower))
            
            if re.search(r'for\s+\w+\s+in\s+range|for\s*\(.*;\s*.*;\s*.*\)|for\s*\(.*\s*:\s*.*\)', code_lower):
                if is_graph and not has_backtrack:
                    return RecursionType.LINEAR # DFS is structurally linear in V+E
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
            # Check for logarithmic loop (i *= 2, i /= 2, i >>= 1)
            if re.search(r'\*=\s*2|/=\s*2|//=\s*2|>>=\s*1|\b\w+\s*=\s*\w+\s*\*|/\s*2', code):
                return "O(log n)"
            # Square root loop (i*i <= n or sqrt(n))
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
        
        # Recursion stack space (Depth of recursion)
        if recursion_type == RecursionType.BINARY:
            space_complexities.append("O(log n)")  # stack depth log n
        elif recursion_type == RecursionType.DIVIDE_CONQUER:
            space_complexities.append("O(n)")  # Merge sort uses O(n) array + O(log n) stack
        elif recursion_type in [RecursionType.LINEAR, RecursionType.EXPONENTIAL]:
            space_complexities.append("O(n)")  # stack depth n
        elif recursion_type == RecursionType.FACTORIAL:
            space_complexities.append("O(n)")  # stack depth n (for permutations)
        
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
        func_pattern = r'(?:public|private|protected|static|final|synchronized|volatile|native|abstract|void|int|bool|string|double|float|auto|[\w<>\b\[\]]+)\s+([\w\d_]+)\s*\(([^)]*)\)\s*(?:throws\s+[\w\s,]+)?\s*\{'
        
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

        code_lower = code.lower()
        
        # Count loops
        loop_matches = list(re.finditer(r'\b(for|while)\s*\(', code))
        loop_count = len(loop_matches)
        
        # Estimate loop depth using brace tracking
        loop_depth = self._estimate_loop_depth(code)
        
        # Detect all external calls in the block and identify constant vs scaling
        external_calls = []
        call_matches = re.finditer(r'\b([a-zA-Z_]\w*)\s*\(([^)]*)\)', code)
        for m in call_matches:
            c_name = m.group(1)
            if c_name == name: continue # skip recursion
            args_str = m.group(2).strip()
            # Constant if empty or only literals/digits (e.g. 8, 20, "ABC")
            # If it contains a word that looks like a variable (n, size, len) -> scaling
            is_const = True
            if args_str:
                if re.search(r'\b(n|m|k|size|len|arr|args)\b', args_str.lower()):
                    is_const = False
                elif not re.match(r'^[\d\s,."\'\-truefalsenull]+$', args_str.lower()):
                    is_const = False
            external_calls.append((c_name, is_const))

        # Detect recursion (self-calls)
        recursion_calls = len([c for c in external_calls if c[0] == name])
        
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
            uses_param_as_bound=uses_param_as_bound
        )
    
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
                # We reached a nesting level
                current_depth += 1
                max_depth = max(max_depth, current_depth)
                loop_starts.append(brace_depth)
            
            # Braces detection
            brace_depth += line.count('{') - line.count('}')
            
            # UN-NESTING LOGIC:
            # If a loop has a brace, we only pop when that brace depth is exited (<).
            # If a loop has NO brace, it technically only lasts for the very next line of logic.
            # Robust heuristic: pop only when brace depth decreases below the start depth.
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
        
        # Check for constant-bounded algorithms
        has_collapsed = False
        collapsed_info = ""
        for f in self.functions:
            if f.time_complexity in ["O(2ⁿ)", "O(n!)", "O(n³)", "O(n²)"]:
                if not any(f.name == wf for wf in worst_funcs) or worst_time == "O(1)":
                    has_collapsed = True
                    collapsed_info = f" (Intrinsic {f.time_complexity} collapsed to O(1) due to constant bounds)"
                    break
        
        if num_funcs == 1:
            return f"Single-purpose implementation. {worst_time} time complexity{collapsed_info if has_collapsed else ''}."
            
        cat_str = f" ({', '.join(categories)})" if categories else ""
        return (
            f"Multiple algorithms detected{cat_str}. "
            f"Worst-case: {worst_time} triggered by {', '.join(worst_funcs)}.{collapsed_info if has_collapsed else ''}"
        )


def analyze_per_function(code: str) -> Dict:
    """
    Main entry point for per-function analysis.
    Returns structured result with per-function breakdown.
    """
    analyzer = PerFunctionAnalyzer(code)
    result = analyzer.analyze()
    
    return {
        "functions": [
            {
                "name": f.name,
                "lineStart": f.line_start,
                "lineEnd": f.line_end,
                "timeComplexity": f.time_complexity,
                "spaceComplexity": f.space_complexity,
                "category": f.category,
                "loopDepth": f.loop_depth,
                "recursionType": f.recursion_type.value,
                "reasoning": f.reasoning
            }
            for f in result.functions
        ],
        "worstTime": result.worst_time,
        "worstSpace": result.worst_space,
        "worstTimeFunction": result.worst_time_function,
        "worstSpaceFunction": result.worst_space_function,
        "complexityLevel": result.complexity_level,
        "summary": result.summary,
        "totalFunctions": len(result.functions)
    }


# Test
if __name__ == "__main__":
    test_code = '''
def constant_op():
    x = 1 + 2
    return x

def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

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

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def permutations(arr, start=0):
    if start == len(arr) - 1:
        print(arr)
        return
    for i in range(start, len(arr)):
        arr[start], arr[i] = arr[i], arr[start]  # swap
        permutations(arr, start + 1)
        arr[start], arr[i] = arr[i], arr[start]  # swap back
'''
    
    result = analyze_per_function(test_code)
    
    print("=" * 60)
    print("PER-FUNCTION COMPLEXITY ANALYSIS")
    print("=" * 60)
    
    for func in result["functions"]:
        print(f"\n{func['name']}() [lines {func['lineStart']}-{func['lineEnd']}]")
        print(f"  Time:  {func['timeComplexity']}")
        print(f"  Space: {func['spaceComplexity']}")
        print(f"  {func['reasoning']}")
    
    print("\n" + "=" * 60)
    print("WORST-CASE SUMMARY (using MAX, not multiply)")
    print("=" * 60)
    print(f"Worst Time:  {result['worstTime']} (from {result['worstTimeFunction']})")
    print(f"Worst Space: {result['worstSpace']} (from {result['worstSpaceFunction']})")
    print(f"Level: {result['complexityLevel']}")
    print(f"Summary: {result['summary']}")
