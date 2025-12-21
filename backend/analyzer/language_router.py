# ==========================================================
# LANGUAGE DETECTION (DETERMINISTIC, NO AI)
# ==========================================================

import re


def detect_language(code: str) -> str:
    """
    Heuristic-based language detection.
    Used to route analysis logic and return accurate language info.
    Priority order: more specific patterns first.
    """
    
    # ---------- JAVA (check before Python - System.out.print contains 'print') ----------
    if re.search(r'public\s+(class|static|void)|private\s+(class|static|void)', code):
        return "Java"
    if re.search(r'System\.out\.print|class\s+\w+\s*\{|void\s+main\s*\(\s*String', code):
        return "Java"
    
    # ---------- C++ (check before C) ----------
    if re.search(r'#include\s*<(iostream|vector|string|algorithm|map|set|queue|stack)>', code):
        return "C++"
    if re.search(r'std::|cout\s*<<|cin\s*>>|using\s+namespace\s+std|nullptr|::\w+\(', code):
        return "C++"
    if re.search(r'template\s*<|std::vector|std::map|std::string', code):
        return "C++"
    
    # ---------- C ----------
    if re.search(r'#include\s*<(stdio|stdlib|string|math|ctype|time)\.h>', code):
        return "C"
    if re.search(r'printf\s*\(|scanf\s*\(|malloc\s*\(|free\s*\(', code):
        return "C"
    if re.search(r'int\s+main\s*\(\s*(void)?\s*\)', code) and '#include' in code:
        return "C"
    
    # ---------- TypeScript (check before JavaScript) ----------
    if re.search(r':\s*(string|number|boolean|void|any|never)\s*[;,\)=\{]', code):
        return "TypeScript"
    if re.search(r'interface\s+\w+\s*\{|type\s+\w+\s*=|<\w+>\s*\(|React\.(FC|Component)', code):
        return "TypeScript"
    
    # ---------- Go ----------
    if re.search(r'^package\s+\w+', code, re.MULTILINE):
        return "Go"
    if re.search(r'func\s+\w+\s*\([^)]*\)\s*\{|:=\s*|fmt\.(Print|Scan)', code):
        return "Go"
    
    # ---------- Rust ----------
    if re.search(r'fn\s+\w+\s*\([^)]*\)\s*(->\s*\w+)?\s*\{', code):
        return "Rust"
    if re.search(r'let\s+mut\s+|println!\s*\(|impl\s+\w+|pub\s+fn|use\s+std::', code):
        return "Rust"
    
    # ---------- PYTHON ----------
    if re.search(r'^\s*def\s+\w+\s*\(', code, re.MULTILINE):
        return "Python"
    if re.search(r'^\s*class\s+\w+\s*:', code, re.MULTILINE):
        return "Python"
    if re.search(r'^\s*import\s+\w+|^\s*from\s+\w+\s+import', code, re.MULTILINE):
        return "Python"
    if re.search(r'(?<![.\w])print\s*\(|^\s*elif\s+', code, re.MULTILINE):
        return "Python"
    if re.search(r'if\s+__name__\s*==\s*["\']__main__["\']', code):
        return "Python"
    
    # ---------- JAVASCRIPT ----------
    if re.search(r'\bfunction\s+\w+\s*\(|\bconst\s+\w+\s*=|\blet\s+\w+\s*=', code):
        return "JavaScript"
    if re.search(r'console\.(log|error|warn)\s*\(|=>\s*[\{\(]', code):
        return "JavaScript"
    if re.search(r'module\.exports|require\s*\([\'"]|document\.|window\.', code):
        return "JavaScript"
    
    # ---------- Ruby ----------
    if re.search(r'^\s*def\s+\w+.*\n.*\n.*^\s*end\s*$', code, re.MULTILINE):
        return "Ruby"
    if re.search(r'puts\s+|require\s+[\'"]|\.each\s+do|attr_(accessor|reader|writer)', code):
        return "Ruby"
    
    # ---------- PHP ----------
    if re.search(r'<\?php|\$\w+\s*=|echo\s+[\'"\$]|\$this->', code):
        return "PHP"
    
    return "Generic"
