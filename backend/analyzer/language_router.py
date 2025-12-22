# ==========================================================
# LANGUAGE DETECTION (DETERMINISTIC, NO AI)
# ==========================================================

import re


def detect_language(code: str) -> str:
    """
    Heuristic-based language detection.
    Used to route analysis logic and return accurate language info.
    Priority order: more specific patterns first.
    
    IMPORTANT: C++ must be checked BEFORE Java because:
    - C++ uses `public:` (access specifier with colon)
    - Java uses `public class` (modifier before keyword)
    """
    
    # ---------- C++ (check BEFORE Java - has public: vs public class) ----------
    if re.search(r'#include\s*<(iostream|vector|string|algorithm|map|set|queue|stack|cstdlib|cstring|cmath)>', code):
        return "C++"
    if re.search(r'std::|cout\s*<<|cin\s*>>|using\s+namespace\s+std|nullptr', code):
        return "C++"
    if re.search(r'template\s*<|std::vector|std::map|std::string|std::queue|std::stack', code):
        return "C++"
    # C++ class with access specifiers (public:, private:, protected:)
    if re.search(r'class\s+\w+\s*\{', code) and re.search(r'\b(public|private|protected)\s*:', code):
        return "C++"
    # C++ style function with references/pointers in signature
    if re.search(r'\w+\s*&\s*\w+|std::\w+|::\w+\s*\(', code):
        return "C++"
    
    # ---------- JAVA (after C++) ----------
    if re.search(r'public\s+(class|static|void|int|String)|private\s+(class|static|void|int|String)', code):
        return "Java"
    if re.search(r'System\.out\.print|void\s+main\s*\(\s*String\s*\[\s*\]', code):
        return "Java"
    # Java package/import
    if re.search(r'^package\s+[\w.]+;|^import\s+java\.', code, re.MULTILINE):
        return "Java"
    
    # ---------- C (check after C++) ----------
    if re.search(r'#include\s*<(stdio|stdlib|string|math|ctype|time|stdbool)\.h>', code):
        return "C"
    if re.search(r'printf\s*\(|scanf\s*\(|malloc\s*\(|free\s*\(', code):
        return "C"
    if re.search(r'int\s+main\s*\(\s*(void|int\s+argc)?\s*[,)]', code) and '#include' in code:
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
    
    # Check if it's actually code or just plain text
    if not is_code(code):
        return "Plain Text"
    
    return "Generic"


def is_code(code: str) -> bool:
    """
    Detect if the input is actual code or just plain text.
    Returns True if code patterns are found, False otherwise.
    """
    if not code or not code.strip():
        return False
    
    # Code indicators - if ANY of these are present, it's likely code
    code_patterns = [
        # Function definitions
        r'\bdef\s+\w+\s*\(',          # Python
        r'\bfunction\s+\w+\s*\(',     # JavaScript
        r'\b(public|private|protected)\s+',  # Java/C++
        r'\bvoid\s+\w+\s*\(',         # C/C++/Java
        r'\bint\s+\w+\s*\(',          # C/C++
        r'\bfn\s+\w+\s*\(',           # Rust
        r'\bfunc\s+\w+\s*\(',         # Go
        
        # Variable declarations
        r'\b(var|let|const)\s+\w+\s*=',  # JS/TS
        r'\bint\s+\w+\s*=',              # C/C++/Java
        r'\bstr\s+\w+\s*=',              # Various
        r'\$\w+\s*=',                    # PHP
        
        # Control structures
        r'\bif\s*\(.+\)\s*\{',        # C-style if
        r'\bfor\s*\(.+\)\s*\{',       # C-style for
        r'\bwhile\s*\(.+\)\s*\{',     # C-style while
        r'\bfor\s+\w+\s+in\s+',       # Python for
        r'\bif\s+.+:',                # Python if
        
        # Imports/Includes
        r'#include\s*<',              # C/C++
        r'\bimport\s+\w+',            # Python/Java/JS
        r'\bfrom\s+\w+\s+import',     # Python
        r'\brequire\s*\(',            # JS/Ruby
        r'\buse\s+\w+::',             # Rust
        
        # Class definitions
        r'\bclass\s+\w+',             # Most languages
        r'\bstruct\s+\w+',            # C/C++/Rust
        r'\binterface\s+\w+',         # Java/TS
        
        # Common code patterns
        r'\breturn\s+',               # Return statements
        r'[;{}]',                     # Braces and semicolons
        r'=>',                        # Arrow functions
        r'->',                        # Arrow operators (PHP, Rust)
        r'::',                        # Scope resolution
        r'\[\s*\w*\s*\]',             # Array access
        r'\w+\s*\(\s*\)',             # Function calls
        r'!=|==|<=|>=|&&|\|\|',       # Comparison operators
        r'\+=|-=|\*=|/=',             # Compound assignment
        
        # Comments (strong indicator of code)
        r'//.*$',                     # Single-line comment
        r'/\*.*\*/',                  # Multi-line comment
        r'#.*$',                      # Hash comment (but check it's not just hashtags)
    ]
    
    # Count how many code patterns match
    matches = 0
    for pattern in code_patterns:
        if re.search(pattern, code, re.MULTILINE):
            matches += 1
    
    # If we have at least 2 code patterns, it's likely code
    if matches >= 2:
        return True
    
    # Additional check: code usually has specific structural elements
    lines = code.strip().split('\n')
    
    # Check for indentation patterns (common in Python, significant in structured code)
    has_indentation = any(line.startswith('    ') or line.startswith('\t') for line in lines if line.strip())
    
    # Check for common code line endings
    has_code_endings = any(line.rstrip().endswith(('{', '}', ';', ':', ')', ',')) for line in lines if line.strip())
    
    # If has indentation AND code patterns OR code endings, it's code
    if has_indentation and (matches >= 1 or has_code_endings):
        return True
    
    # Check ratio of special characters (code has more)
    total_chars = len(code.replace(' ', '').replace('\n', ''))
    if total_chars == 0:
        return False
    
    special_chars = len(re.findall(r'[{}\[\]();:=<>!&|+\-*/%]', code))
    special_ratio = special_chars / total_chars
    
    # Code typically has >5% special characters
    if special_ratio > 0.05 and matches >= 1:
        return True
    
    return False
