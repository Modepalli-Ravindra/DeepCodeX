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
    
    # Complexity ordering for comparison
    COMPLEXITY_ORDER = {
        "O(1)": 0,
        "O(log n)": 1,
        "O(√n)": 2,
        "O(n)": 3,
        "O(n log n)": 4,
        "O(n²)": 5,
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
        
        # Compute worst-case using MAX (not multiply!)
        worst_time = self._get_worst_complexity([f.time_complexity for f in self.functions])
        worst_space = self._get_worst_complexity([f.space_complexity for f in self.functions])
        
        worst_time_func = next(
            (f.name for f in self.functions if f.time_complexity == worst_time),
            self.functions[0].name if self.functions else "unknown"
        )
        worst_space_func = next(
            (f.name for f in self.functions if f.space_complexity == worst_space),
            self.functions[0].name if self.functions else "unknown"
        )
        
        # Determine complexity level
        level = self._get_complexity_level(worst_time)
        
        # Generate summary
        summary = self._generate_summary(worst_time, worst_space, worst_time_func)
        
        return AnalysisResult(
            functions=self.functions,
            worst_time=worst_time,
            worst_space=worst_space,
            worst_time_function=worst_time_func,
            worst_space_function=worst_space_func,
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
                self.recursion_calls = 0
                self.has_loop_in_recursion = False
                self.in_recursion = False
                self.allocations = []
            
            def visit_For(self, n):
                self.loop_count += 1
                self.loop_depth += 1
                self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
                if self.in_recursion:
                    self.has_loop_in_recursion = True
                self.generic_visit(n)
                self.loop_depth -= 1
            
            def visit_While(self, n):
                self.loop_count += 1
                self.loop_depth += 1
                self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
                if self.in_recursion:
                    self.has_loop_in_recursion = True
                self.generic_visit(n)
                self.loop_depth -= 1
            
            def visit_Call(self, n):
                if isinstance(n.func, ast.Name) and n.func.id == func_name:
                    self.recursion_calls += 1
                    self.in_recursion = True
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
            loop_depth, recursion_type, recursion_calls, time_complexity
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
            reasoning=reasoning
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
        
        # Check for FACTORIAL pattern: permutation with swap
        if (re.search(r'permut', code_lower) and 
            re.search(r'swap|\.append|result', code_lower) and
            recursion_calls >= 1):
            return RecursionType.FACTORIAL
        
        # Check for swap-based permutation (backtracking)
        if (re.search(r'for\s+\w+\s+in\s+range', code_lower) and
            re.search(r'swap', code_lower) and recursion_calls >= 1):
            return RecursionType.FACTORIAL
        
        # Check for EXPONENTIAL: multiple recursive calls like Fibonacci
        if recursion_calls >= 2:
            # f(n-1) + f(n-2) pattern
            if re.search(rf'{func_name}\s*\([^)]*-\s*1[^)]*\).*{func_name}\s*\([^)]*-\s*2', code):
                return RecursionType.EXPONENTIAL
            # General: 2+ recursive calls without merge
            if not re.search(r'merge|left|right|mid', code_lower):
                return RecursionType.EXPONENTIAL
        
        # Check for DIVIDE_CONQUER: recursion with n/2 + merge
        if (re.search(r'/\s*2|//\s*2|>>\s*1', code) and 
            re.search(r'merge|left|right', code_lower)):
            return RecursionType.DIVIDE_CONQUER
        
        # Check for BINARY: single recursion with n/2
        if (recursion_calls == 1 and 
            re.search(r'/\s*2|//\s*2|>>\s*1', code)):
            return RecursionType.BINARY
        
        # Default: LINEAR recursion f(n-1)
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
            # Check for logarithmic loop
            if re.search(r'/=\s*2|//=\s*2|>>=\s*1', code):
                return "O(log n)"
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
        
        # Check for 2D array/matrix
        if re.search(r'\[\s*\[|matrix|\[\w+\]\[\w+\]', code.lower()):
            space_complexities.append("O(n²)")
        
        # Check for DP table
        if re.search(r'dp\s*\[|memo\s*\[|table\s*\[', code.lower()):
            if re.search(r'\]\s*\[', code):  # 2D
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
            space_complexities.append("O(n)")  # Merge sort uses O(n)
        elif recursion_type in [RecursionType.LINEAR, RecursionType.EXPONENTIAL]:
            space_complexities.append("O(n)")
        elif recursion_type == RecursionType.FACTORIAL:
            space_complexities.append("O(n)")  # Stack depth is n
        
        if not space_complexities:
            return "O(1)"
        
        # Return MAX (not sum!)
        return self._get_worst_complexity(space_complexities)
    
    def _generate_reasoning(self, loop_depth: int, 
                           recursion_type: RecursionType,
                           recursion_calls: int, 
                           time_complexity: str) -> str:
        """Generate human-readable reasoning."""
        reasons = []
        
        if loop_depth > 0:
            reasons.append(f"{loop_depth} nested loop(s)")
        
        if recursion_type != RecursionType.NONE:
            type_desc = {
                RecursionType.LINEAR: "linear recursion f(n-1)",
                RecursionType.BINARY: "binary recursion f(n/2)",
                RecursionType.DIVIDE_CONQUER: "divide & conquer",
                RecursionType.EXPONENTIAL: "exponential branching",
                RecursionType.FACTORIAL: "permutation recursion"
            }
            reasons.append(type_desc.get(recursion_type, str(recursion_type.value)))
        
        if not reasons:
            reasons.append("constant-time operations")
        
        return f"{time_complexity} because: {', '.join(reasons)}"
    
    def _analyze_generic(self):
        """Analyze non-Python code by detecting function boundaries."""
        # Pattern for function definitions
        func_pattern = r'(?:void|int|bool|string|double|float|auto|\w+)\s+(\w+)\s*\([^)]*\)\s*\{'
        
        lines = self.code.split('\n')
        current_func = None
        func_start = 0
        brace_depth = 0
        func_body_lines = []
        
        for i, line in enumerate(lines, 1):
            match = re.search(func_pattern, line)
            
            if match and brace_depth == 0:
                current_func = match.group(1)
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
                        current_func, func_code, func_start, i
                    )
                    self.functions.append(analysis)
                    current_func = None
                    func_body_lines = []
    
    def _analyze_code_block(self, name: str, code: str, 
                           line_start: int, line_end: int) -> FunctionComplexity:
        """Analyze a generic code block."""
        code_lower = code.lower()
        
        # Count loops
        loop_matches = list(re.finditer(r'\b(for|while)\s*\(', code))
        loop_count = len(loop_matches)
        
        # Estimate loop depth using brace tracking
        loop_depth = self._estimate_loop_depth(code)
        
        # Detect recursion
        func_calls = re.findall(rf'\b{re.escape(name)}\s*\(', code[len(name)+10:])  # Skip definition
        recursion_calls = len(func_calls)
        
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
        
        reasoning = self._generate_reasoning(
            loop_depth, recursion_type, recursion_calls, time_complexity
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
            reasoning=reasoning
        )
    
    def _estimate_loop_depth(self, code: str) -> int:
        """Estimate maximum nested loop depth."""
        max_depth = 0
        current_depth = 0
        loop_starts = []
        brace_depth = 0
        
        for line in code.split('\n'):
            if re.search(r'\b(for|while)\s*\(', line):
                loop_starts.append(brace_depth)
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            
            brace_depth += line.count('{') - line.count('}')
            
            while loop_starts and brace_depth <= loop_starts[-1]:
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
                         worst_func: str) -> str:
        """Generate analysis summary."""
        if len(self.functions) == 1:
            return f"Single function with {worst_time} time complexity"
        
        return (
            f"Multiple algorithms detected ({len(self.functions)} functions). "
            f"Worst-case: {worst_time} from '{worst_func}'"
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
