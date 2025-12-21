import ast
import re
from typing import Dict


# ==========================================================
# PYTHON STRUCTURAL ANALYZER (AST ONLY)
# ==========================================================

class PythonMetrics(ast.NodeVisitor):
    def __init__(self):
        # counts
        self.functions = 0
        self.conditions = 0
        self.cyclomatic = 1

        # loops
        self.loop_count = 0
        self.current_loop_depth = 0
        self.max_loop_depth = 0
        self.has_log_loop = False

        # space
        self.dynamic_allocations = 0

        # recursion
        self.current_function = None
        self.has_recursion = False
        self.multi_recursion = False
        self.recursive_calls = 0

    # ---------- FUNCTIONS ----------

    def visit_FunctionDef(self, node):
        prev = self.current_function
        self.current_function = node.name

        self.functions += 1
        self.cyclomatic += 1
        self.generic_visit(node)

        self.current_function = prev

    # ---------- LOOPS ----------

    def visit_For(self, node):
        self._enter_loop()
        self.generic_visit(node)
        self._exit_loop()

    def visit_While(self, node):
        self._enter_loop()

        # logarithmic update detection (n//=2, n/=2, >>)
        for stmt in node.body:
            if isinstance(stmt, (ast.Assign, ast.AugAssign)):
                if any(op in ast.dump(stmt) for op in ("FloorDiv", "Div", "RShift")):
                    self.has_log_loop = True

        self.generic_visit(node)
        self._exit_loop()

    # ---------- CONDITIONS ----------

    def visit_If(self, node):
        self.conditions += 1
        self.cyclomatic += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.cyclomatic += max(len(node.values) - 1, 0)
        self.generic_visit(node)

    # ---------- CALLS / SPACE / RECURSION ----------

    def visit_Call(self, node):
        # recursion detection
        if isinstance(node.func, ast.Name) and node.func.id == self.current_function:
            self.has_recursion = True
            self.recursive_calls += 1
            if self.recursive_calls > 1:
                self.multi_recursion = True

        # dynamic memory growth
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ("append", "extend", "add", "insert"):
                self.dynamic_allocations += 1

        self.generic_visit(node)

    def visit_ListComp(self, node):
        self.dynamic_allocations += 1
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self.dynamic_allocations += 1
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self.dynamic_allocations += 1
        self.generic_visit(node)

    # ---------- INTERNAL ----------

    def _enter_loop(self):
        self.loop_count += 1
        self.cyclomatic += 1
        self.current_loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)

    def _exit_loop(self):
        self.current_loop_depth -= 1


# ==========================================================
# GENERIC STRUCTURAL ANALYZER (C / C++ / JAVA / JS)
# WITH IMPROVED LOOP DEPTH DETECTION
# ==========================================================

class GenericMetrics:
    LOOP_RE = re.compile(r"\b(for|while)\b")
    IF_RE = re.compile(r"\b(if|else if|switch)\b")
    FUNC_RE = re.compile(r"\b[a-zA-Z_]\w*\s*\(")
    ALLOC_RE = re.compile(r"\b(new|malloc|calloc|realloc|push|append|Map|Set|vector)\b")
    LOG_RE = re.compile(r"/\s*2|>>|left\s*\+|right\s*-")

    def __init__(self, code: str):
        self.code = code
        self.lines = [l for l in code.splitlines() if l.strip()]

    def analyze(self) -> Dict:
        loops = len(self.LOOP_RE.findall(self.code))
        conditions = len(self.IF_RE.findall(self.code))
        allocations = len(self.ALLOC_RE.findall(self.code))
        has_log = bool(self.LOG_RE.search(self.code))

        # Improved loop depth detection using brace/indentation analysis
        max_loop_depth = self._detect_loop_depth()

        # recursion detection (conservative)
        funcs = re.findall(r"\b([a-zA-Z_]\w*)\s*\(", self.code)
        
        # Use regex to count to handle spaces like "func ("
        def count_calls(fn_name):
            return len(re.findall(rf"\b{re.escape(fn_name)}\s*\(", self.code))

        recursion = any(count_calls(fn) > 1 for fn in funcs)
        multi_rec = any(count_calls(fn) > 2 for fn in funcs)

        return {
            "linesOfCode": len(self.lines),
            "functionCount": len(set(funcs)),
            "loopCount": loops,
            "conditionalCount": conditions,
            "cyclomaticComplexity": max(1 + loops + conditions, 1),
            "dynamicAllocations": allocations,
            "maxLoopDepth": max_loop_depth,
            "hasLogLoop": has_log,
            "hasRecursion": recursion,
            "multiRecursion": multi_rec,
            "language": "Generic",
        }

    def _detect_loop_depth(self) -> int:
        """
        Detect maximum nested loop depth by tracking braces after loop keywords.
        Works for C, C++, Java, JavaScript.
        """
        max_depth = 0
        current_depth = 0
        in_loop_stack = []  # Track brace depth when entering loops
        brace_depth = 0

        lines = self.code.split('\n')
        
        for line in lines:
            # Count braces
            open_braces = line.count('{')
            close_braces = line.count('}')
            
            # Check for loop start
            if re.search(r'\b(for|while)\s*\(', line):
                in_loop_stack.append(brace_depth + open_braces)
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            
            brace_depth += open_braces - close_braces
            
            # Check if we've exited loops
            while in_loop_stack and brace_depth < in_loop_stack[-1]:
                in_loop_stack.pop()
                current_depth -= 1

        # Fallback: if no depth detected but we have loops, estimate from loop count
        if max_depth == 0 and self.LOOP_RE.search(self.code):
            # Simple heuristic: if loops exist close together, they might be nested
            loop_positions = [m.start() for m in self.LOOP_RE.finditer(self.code)]
            if len(loop_positions) >= 3:
                # Check if loops are within reasonable proximity (likely nested)
                for i in range(len(loop_positions) - 2):
                    if loop_positions[i+2] - loop_positions[i] < 500:
                        max_depth = 3
                        break
                else:
                    for i in range(len(loop_positions) - 1):
                        if loop_positions[i+1] - loop_positions[i] < 300:
                            max_depth = max(max_depth, 2)
                    if max_depth == 0:
                        max_depth = 1
            elif len(loop_positions) == 2:
                if loop_positions[1] - loop_positions[0] < 300:
                    max_depth = 2
                else:
                    max_depth = 1
            else:
                max_depth = 1

        return max_depth


# ==========================================================
# ENTRY POINT
# ==========================================================

def analyze_static(code: str, language: str = "auto") -> Dict:
    try:
        tree = ast.parse(code)
        metrics = PythonMetrics()
        metrics.visit(tree)

        return {
            "linesOfCode": len([l for l in code.splitlines() if l.strip()]),
            "functionCount": metrics.functions,
            "loopCount": metrics.loop_count,
            "conditionalCount": metrics.conditions,
            "cyclomaticComplexity": metrics.cyclomatic,
            "dynamicAllocations": metrics.dynamic_allocations,
            "maxLoopDepth": metrics.max_loop_depth,
            "hasLogLoop": metrics.has_log_loop,
            "hasRecursion": metrics.has_recursion,
            "multiRecursion": metrics.multi_recursion,
            "language": "Python",
        }

    except SyntaxError:
        return GenericMetrics(code).analyze()
