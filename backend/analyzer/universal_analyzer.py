"""
🧮 Universal Complexity Analyzer
================================
Based on the mathematical formula:
T(n) = Σ Cᵢ·fᵢ(n) → max{f₁(n), f₂(n), ..., fₗ(n)}
S(n) = Σ Mᵢ·gᵢ(n) → max{g₁(n), g₂(n), ..., gₗ(n)}

This analyzer works for 500-1000+ lines by classifying growth patterns.
"""

import ast
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math


class LineClassification(Enum):
    """Classification types for code lines/blocks"""
    CONSTANT_OPERATION = "constant"
    LOOP = "loop"
    NESTED_LOOP = "nested_loop"
    RECURSION = "recursion"
    MULTI_RECURSION = "multi_recursion"
    DATA_STRUCTURE = "data_structure"
    DIVIDE_CONQUER = "divide_conquer"
    LOGARITHMIC_LOOP = "log_loop"


@dataclass
class ComplexityTerm:
    """Represents a complexity term like O(n), O(n²), O(log n)"""
    base: str  # "1", "n", "log n", "n log n", "n²", "2^n", "n!"
    coefficient: int = 1
    exponent: int = 1
    
    def __str__(self):
        if self.base == "1":
            return "O(1)"
        elif self.base == "n" and self.exponent == 1:
            return "O(n)"
        elif self.base == "n" and self.exponent == 2:
            return "O(n²)"
        elif self.base == "n" and self.exponent == 3:
            return "O(n³)"
        elif self.base == "n" and self.exponent > 3:
            return f"O(n^{self.exponent})"
        else:
            return f"O({self.base})"
    
    def dominates(self, other: "ComplexityTerm") -> bool:
        """Check if this term dominates another"""
        order = {
            "1": 0,
            "log n": 1,
            "√n": 2,
            "n": 3,
            "n log n": 4,
            "n²": 5,
            "n³": 6,
            "2^n": 7,
            "n!": 8
        }
        
        self_key = self._to_key()
        other_key = other._to_key()
        
        return order.get(self_key, 3) >= order.get(other_key, 3)
    
    def _to_key(self) -> str:
        if self.base == "1":
            return "1"
        elif self.base == "log n":
            return "log n"
        elif self.base == "√n":
            return "√n"
        elif self.base == "n" and self.exponent == 1:
            return "n"
        elif self.base == "n log n":
            return "n log n"
        elif self.base == "n" and self.exponent == 2:
            return "n²"
        elif self.base == "n" and self.exponent == 3:
            return "n³"
        elif self.base == "2^n":
            return "2^n"
        elif self.base == "n!":
            return "n!"
        else:
            return "n"


@dataclass
class LineAnalysis:
    """Analysis result for a single line/block"""
    line_number: int
    classification: LineClassification
    time_complexity: ComplexityTerm
    space_complexity: ComplexityTerm
    description: str


class UniversalComplexityAnalyzer:
    """
    Implements the universal formula for complexity analysis:
    T(n) = max{f₁(n), f₂(n), ..., fₗ(n)}
    S(n) = max{g₁(n), g₂(n), ..., gₗ(n)}
    """
    
    def __init__(self, code: str):
        self.code = code
        self.lines = code.split('\n')
        self.line_analyses: List[LineAnalysis] = []
        self.current_loop_depth = 0
        self.max_loop_depth = 0
        self.has_recursion = False
        self.recursion_count = 0
        self.function_names: List[str] = []
        self.data_structures: List[str] = []
        
    def analyze(self) -> Dict:
        """
        Main analysis algorithm following the pseudocode:
        1. Initialize
        2. For each line/block: classify and assign f(n), g(n)
        3. Return dominant terms
        """
        # Step 1: Initialize
        dominant_time = ComplexityTerm(base="1")
        dominant_space = ComplexityTerm(base="1")
        
        # Pre-scan to identify functions for recursion detection
        self._scan_functions()
        
        # Step 2: Analyze each line/block
        try:
            # Try AST-based analysis for Python
            tree = ast.parse(self.code)
            self._analyze_ast(tree)
        except SyntaxError:
            # Fallback to regex-based analysis for other languages
            self._analyze_generic()
        
        # Step 3: Find dominant terms
        for analysis in self.line_analyses:
            if analysis.time_complexity.dominates(dominant_time):
                dominant_time = analysis.time_complexity
            if analysis.space_complexity.dominates(dominant_space):
                dominant_space = analysis.space_complexity
        
        # Build result
        return {
            "timeComplexity": str(dominant_time),
            "spaceComplexity": str(dominant_space),
            "lineAnalyses": [
                {
                    "line": a.line_number,
                    "type": a.classification.value,
                    "time": str(a.time_complexity),
                    "space": str(a.space_complexity),
                    "description": a.description
                }
                for a in self.line_analyses[:20]  # Limit for display
            ],
            "totalLines": len(self.lines),
            "maxLoopDepth": self.max_loop_depth,
            "hasRecursion": self.has_recursion,
            "recursionCount": self.recursion_count,
            "formula": f"T(n) = max{{{', '.join(set(str(a.time_complexity) for a in self.line_analyses))}}} = {dominant_time}",
            "spaceFormula": f"S(n) = max{{{', '.join(set(str(a.space_complexity) for a in self.line_analyses))}}} = {dominant_space}"
        }
    
    def _scan_functions(self):
        """Pre-scan to identify function names for recursion detection"""
        # Python functions
        py_funcs = re.findall(r'def\s+(\w+)\s*\(', self.code)
        self.function_names.extend(py_funcs)
        
        # Java/C++ methods
        java_funcs = re.findall(r'(?:public|private|protected|static)?\s*(?:\w+)\s+(\w+)\s*\([^)]*\)\s*\{', self.code)
        self.function_names.extend(java_funcs)
        
        # JavaScript functions
        js_funcs = re.findall(r'function\s+(\w+)\s*\(', self.code)
        self.function_names.extend(js_funcs)
        
        # C functions
        c_funcs = re.findall(r'\b(\w+)\s*\([^)]*\)\s*\{', self.code)
        self.function_names.extend(c_funcs)
    
    def _analyze_ast(self, tree: ast.AST):
        """Analyze Python code using AST"""
        
        class ASTAnalyzer(ast.NodeVisitor):
            def __init__(self, parent):
                self.parent = parent
                self.loop_depth = 0
                self.current_function = None
            
            def visit_FunctionDef(self, node):
                prev_func = self.current_function
                self.current_function = node.name
                self.generic_visit(node)
                self.current_function = prev_func
            
            def visit_For(self, node):
                self.loop_depth += 1
                self.parent.max_loop_depth = max(self.parent.max_loop_depth, self.loop_depth)
                
                # Classify the loop
                loop_bound = self._extract_loop_bound(node)
                
                if self.loop_depth == 1:
                    classification = LineClassification.LOOP
                    time = ComplexityTerm(base="n", exponent=1)
                else:
                    classification = LineClassification.NESTED_LOOP
                    time = ComplexityTerm(base="n", exponent=self.loop_depth)
                
                self.parent.line_analyses.append(LineAnalysis(
                    line_number=node.lineno,
                    classification=classification,
                    time_complexity=time,
                    space_complexity=ComplexityTerm(base="1"),
                    description=f"Loop depth {self.loop_depth}, bound: {loop_bound}"
                ))
                
                self.generic_visit(node)
                self.loop_depth -= 1
            
            def visit_While(self, node):
                self.loop_depth += 1
                self.parent.max_loop_depth = max(self.parent.max_loop_depth, self.loop_depth)
                
                # Check for logarithmic loop (n //= 2, n /= 2, etc.)
                is_log_loop = self._is_logarithmic_loop(node)
                
                if is_log_loop:
                    classification = LineClassification.LOGARITHMIC_LOOP
                    time = ComplexityTerm(base="log n")
                elif self.loop_depth == 1:
                    classification = LineClassification.LOOP
                    time = ComplexityTerm(base="n", exponent=1)
                else:
                    classification = LineClassification.NESTED_LOOP
                    time = ComplexityTerm(base="n", exponent=self.loop_depth)
                
                self.parent.line_analyses.append(LineAnalysis(
                    line_number=node.lineno,
                    classification=classification,
                    time_complexity=time,
                    space_complexity=ComplexityTerm(base="1"),
                    description=f"While loop, depth {self.loop_depth}" + (" (logarithmic)" if is_log_loop else "")
                ))
                
                self.generic_visit(node)
                self.loop_depth -= 1
            
            def visit_Call(self, node):
                # Check for recursion
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name == self.current_function and self.current_function:
                        self.parent.has_recursion = True
                        self.parent.recursion_count += 1
                        
                        # Determine if it's divide-and-conquer
                        if self.parent.recursion_count > 1:
                            classification = LineClassification.MULTI_RECURSION
                            time = ComplexityTerm(base="2^n")
                        else:
                            # Check for divide-and-conquer pattern
                            if self._is_divide_conquer():
                                classification = LineClassification.DIVIDE_CONQUER
                                time = ComplexityTerm(base="n log n")
                            else:
                                classification = LineClassification.RECURSION
                                time = ComplexityTerm(base="n")
                        
                        self.parent.line_analyses.append(LineAnalysis(
                            line_number=node.lineno,
                            classification=classification,
                            time_complexity=time,
                            space_complexity=ComplexityTerm(base="n") if classification != LineClassification.DIVIDE_CONQUER else ComplexityTerm(base="log n"),
                            description=f"Recursive call to {func_name}"
                        ))
                
                self.generic_visit(node)
            
            def visit_List(self, node):
                # List creation
                self.parent.line_analyses.append(LineAnalysis(
                    line_number=getattr(node, 'lineno', 0),
                    classification=LineClassification.DATA_STRUCTURE,
                    time_complexity=ComplexityTerm(base="1"),
                    space_complexity=ComplexityTerm(base="n"),
                    description="List allocation"
                ))
                self.generic_visit(node)
            
            def visit_ListComp(self, node):
                # List comprehension
                self.parent.line_analyses.append(LineAnalysis(
                    line_number=node.lineno,
                    classification=LineClassification.DATA_STRUCTURE,
                    time_complexity=ComplexityTerm(base="n"),
                    space_complexity=ComplexityTerm(base="n"),
                    description="List comprehension"
                ))
                self.generic_visit(node)
            
            def visit_Dict(self, node):
                self.parent.line_analyses.append(LineAnalysis(
                    line_number=getattr(node, 'lineno', 0),
                    classification=LineClassification.DATA_STRUCTURE,
                    time_complexity=ComplexityTerm(base="1"),
                    space_complexity=ComplexityTerm(base="n"),
                    description="Dictionary allocation"
                ))
                self.generic_visit(node)
            
            def _extract_loop_bound(self, node) -> str:
                """Extract loop bound (e.g., 'n', 'len(arr)')"""
                if isinstance(node.iter, ast.Call):
                    if isinstance(node.iter.func, ast.Name):
                        if node.iter.func.id == 'range':
                            if node.iter.args:
                                return ast.dump(node.iter.args[-1])
                return "n"
            
            def _is_logarithmic_loop(self, node) -> bool:
                """Check if while loop has logarithmic behavior (n //= 2, etc.)"""
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.AugAssign):
                        if isinstance(stmt.op, (ast.FloorDiv, ast.Div, ast.RShift)):
                            return True
                return False
            
            def _is_divide_conquer(self) -> bool:
                """Check for divide and conquer pattern"""
                # Look for mid calculation or array slicing
                code_lower = self.parent.code.lower()
                return any(term in code_lower for term in ['mid', 'left', 'right', 'merge', 'pivot', '//2', '/2'])
        
        analyzer = ASTAnalyzer(self)
        analyzer.visit(tree)
        
        # Add constant operations for remaining lines
        analyzed_lines = {a.line_number for a in self.line_analyses}
        for i, line in enumerate(self.lines, 1):
            if i not in analyzed_lines and line.strip() and not line.strip().startswith('#'):
                self.line_analyses.append(LineAnalysis(
                    line_number=i,
                    classification=LineClassification.CONSTANT_OPERATION,
                    time_complexity=ComplexityTerm(base="1"),
                    space_complexity=ComplexityTerm(base="1"),
                    description="Constant operation"
                ))
    
    def _analyze_generic(self):
        """Analyze non-Python code using regex patterns"""
        
        # Track loop depth using brace counting
        brace_depth = 0
        in_loop_depths = []
        current_loop_depth = 0
        
        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if not stripped:
                continue
            
            # Count braces
            open_braces = line.count('{')
            close_braces = line.count('}')
            
            # Check for loop start
            if re.search(r'\b(for|while)\s*\(', line):
                current_loop_depth += 1
                in_loop_depths.append(brace_depth + open_braces)
                self.max_loop_depth = max(self.max_loop_depth, current_loop_depth)
                
                # Check for logarithmic loop
                is_log = bool(re.search(r'/\s*2|>>\s*1|left\s*\+|right\s*-', line))
                
                if is_log:
                    classification = LineClassification.LOGARITHMIC_LOOP
                    time = ComplexityTerm(base="log n")
                elif current_loop_depth == 1:
                    classification = LineClassification.LOOP
                    time = ComplexityTerm(base="n")
                else:
                    classification = LineClassification.NESTED_LOOP
                    time = ComplexityTerm(base="n", exponent=current_loop_depth)
                
                self.line_analyses.append(LineAnalysis(
                    line_number=i,
                    classification=classification,
                    time_complexity=time,
                    space_complexity=ComplexityTerm(base="1"),
                    description=f"Loop at depth {current_loop_depth}"
                ))
            
            # Check for recursion
            for func_name in self.function_names:
                pattern = rf'\b{re.escape(func_name)}\s*\('
                if re.search(pattern, line):
                    # Count occurrences in entire code
                    call_count = len(re.findall(pattern, self.code))
                    if call_count > 1:  # Called more than once (definition + calls)
                        self.has_recursion = True
                        self.recursion_count = call_count - 1
                        
                        # Check for divide-and-conquer
                        code_lower = self.code.lower()
                        if any(term in code_lower for term in ['mid', 'merge', 'pivot', 'partition']):
                            time = ComplexityTerm(base="n log n")
                            space = ComplexityTerm(base="log n")
                            classification = LineClassification.DIVIDE_CONQUER
                        elif call_count > 2:
                            time = ComplexityTerm(base="2^n")
                            space = ComplexityTerm(base="n")
                            classification = LineClassification.MULTI_RECURSION
                        else:
                            time = ComplexityTerm(base="n")
                            space = ComplexityTerm(base="n")
                            classification = LineClassification.RECURSION
                        
                        self.line_analyses.append(LineAnalysis(
                            line_number=i,
                            classification=classification,
                            time_complexity=time,
                            space_complexity=space,
                            description=f"Recursive call to {func_name}"
                        ))
                        break
            
            # Check for data structure allocations
            if re.search(r'\bnew\s+\w+\[|malloc\s*\(|calloc\s*\(|vector\s*<|ArrayList|HashMap|new\s+Array', line):
                self.line_analyses.append(LineAnalysis(
                    line_number=i,
                    classification=LineClassification.DATA_STRUCTURE,
                    time_complexity=ComplexityTerm(base="1"),
                    space_complexity=ComplexityTerm(base="n"),
                    description="Dynamic memory allocation"
                ))
            
            # Check for 2D array
            if re.search(r'\[\w+\]\[\w+\]|new\s+\w+\[\w+\]\[\w+\]', line):
                self.line_analyses.append(LineAnalysis(
                    line_number=i,
                    classification=LineClassification.DATA_STRUCTURE,
                    time_complexity=ComplexityTerm(base="1"),
                    space_complexity=ComplexityTerm(base="n", exponent=2),
                    description="2D array allocation"
                ))
            
            # Update brace depth
            brace_depth += open_braces - close_braces
            
            # Check if we've exited loops
            while in_loop_depths and brace_depth < in_loop_depths[-1]:
                in_loop_depths.pop()
                current_loop_depth -= 1
        
        # Add constant operations for remaining lines
        analyzed_lines = {a.line_number for a in self.line_analyses}
        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if i not in analyzed_lines and stripped and not stripped.startswith('//') and not stripped.startswith('#'):
                self.line_analyses.append(LineAnalysis(
                    line_number=i,
                    classification=LineClassification.CONSTANT_OPERATION,
                    time_complexity=ComplexityTerm(base="1"),
                    space_complexity=ComplexityTerm(base="1"),
                    description="Constant operation"
                ))


def analyze_with_formula(code: str) -> Dict:
    """
    Main entry point for formula-based analysis.
    Implements: T(n) = max{f₁(n), ..., fₗ(n)}
                S(n) = max{g₁(n), ..., gₗ(n)}
    """
    analyzer = UniversalComplexityAnalyzer(code)
    return analyzer.analyze()


# Test
if __name__ == "__main__":
    test_code = '''
def example(arr):
    n = len(arr)          # constant
    for i in range(n):    # loop O(n)
        for j in range(n):# nested loop O(n^2)
            print(arr[i], arr[j])  # constant
    return sum(arr)       # loop O(n)
'''
    
    result = analyze_with_formula(test_code)
    print(f"Time Complexity: {result['timeComplexity']}")
    print(f"Space Complexity: {result['spaceComplexity']}")
    print(f"Formula: {result['formula']}")
    print(f"\nLine-by-line analysis:")
    for la in result['lineAnalyses']:
        print(f"  Line {la['line']}: {la['type']} → Time: {la['time']}, Space: {la['space']}")
