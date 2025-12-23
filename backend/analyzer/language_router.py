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
    
    # FIRST: Check if it's plain text (not code)
    if not is_code(code):
        return "Plain Text"
    
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
    
    return "Generic"


def is_code(code: str) -> bool:
    """
    Detect if the input is actual code or just plain text.
    Returns True if code patterns are found, False otherwise.
    
    KEY INSIGHT: If text has embedded code snippets but is mostly prose,
    it should be considered text (like documentation or tutorials).
    """
    if not code or not code.strip():
        return False
    
    lines = code.strip().split('\n')
    non_empty_lines = [l.strip() for l in lines if l.strip()]
    
    if len(non_empty_lines) < 2:
        # Very short - check for basic code patterns
        text = code.strip()
        # Stricter checks for single-line code
        if re.match(r'^(def|function)\s+\w+\s*\(', text) or re.match(r'^function\s*\(', text):
            return True
        if re.match(r'^class\s+[A-Z]\w*\s*[:{]', text):
            return True
        if re.match(r'^(public|private)\s+(class|static|void|int|bool|function)\s+\w+', text):
            return True
        # Common single-line statements
        if re.match(r'^(import|#include|package|using)\s+', text) or re.match(r'^from\s+\w+\s+import\s+', text):
            return True
        if re.search(r'^(console\.log|System\.out\.print|print|echo|fmt\.Print)\s*\(', text):
            return True
        if re.match(r'^\w+\s*=\s*(\[|\{|new\s+|FUNCTION|class)', text): # Assignment of complex types
             return True
        return False
    
    # ============================================
    # COUNT PROSE vs CODE LINES
    # ============================================
    
    prose_lines = 0
    code_lines = 0
    
    for line in non_empty_lines:
        is_prose = False
        is_code_line = False
        
        # === STRONG PROSE INDICATORS ===
        
        # Sentence-like (starts capital, ends punctuation, has spaces)
        if re.match(r'^[A-Z][a-zA-Z\s,\'"]+[.!?]$', line) and ' ' in line:
            is_prose = True
        
        # Contains common prose phrases
        # NOTE: Avoid matching common variable names (right, left, method)
        prose_phrases = [
            r'\b(your|you\'re|what\'s|here\'s|that\'s|it\'s|there\'s)\b',
            r'\b(how to|what is|this is|to solve|the problem|the issue)\b',
            r'\b(because|therefore|however|although|instead)\b',
            r'\b(example|tutorial|learn|understand|explain)\b',
        ]
        # Only check prose phrases if line doesn't have obvious code structure
        if not re.search(r'[=\[\]{}();]', line):
            for phrase in prose_phrases:
                if re.search(phrase, line.lower()):
                    is_prose = True
                    break
        
        # Bullet points or numbered lists
        if re.match(r'^[•\-\*✅❌]\s+', line) or re.match(r'^\d+\.\s+[A-Z]', line):
            is_prose = True
        
        # Headers (ALLCAPS or Title Case without code)
        if re.match(r'^[A-Z][A-Z\s]+$', line) or re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)+$', line):
            is_prose = True
        
        # Lines with complexity notation in prose (O(n), O(n²))
        if re.search(r'O\([^\)]+\)', line) and not re.search(r'[{};=]', line):
            is_prose = True
        
        # Short lines that are just words (not code)
        if len(line) < 30 and re.match(r'^[a-zA-Z\s]+$', line) and not re.match(r'^(if|for|while|def|class|return|import|from)\s', line):
            is_prose = True
        
        # === STRONG CODE INDICATORS ===
        
        # Function/class definitions (More strict)
        # def name( OR function name( OR class Name:/{
        if re.match(r'^\s*def\s+\w+\s*\(', line): 
            is_code_line = True
        elif re.match(r'^\s*function\s+(\w+\s*)?\(', line):
            is_code_line = True
        elif re.match(r'^\s*class\s+[A-Z]\w*', line) and re.search(r'[:{\(]', line):
            is_code_line = True
        elif re.match(r'^\s*(class|interface|struct)\s+\w+\s*[{:]', line):
            is_code_line = True
        
        # Access modifiers (must be followed by keywords or types)
        # public static, private void, public ClassName
        if re.match(r'^\s*(public|private|protected)\s+(static|final|abstract|void|class|int|bool|string|function|def)\b', line, re.IGNORECASE):
            is_code_line = True
        elif re.match(r'^\s*(public|private|protected)\s+[A-Z]\w+', line): # Type name usually capped
             is_code_line = True

        # Control structures (support Python style without parens)
        # stricter: require : or { or ( for some, or ensure e.g. 'if' is not 'if I...'
        if re.match(r'^\s*(if|for|while|elif|else|switch|catch)\s*\(', line): # C-style with parens
            is_code_line = True
        elif re.match(r'^\s*(if|elif|while|with)\s+.*:\s*$', line): # Python style with colon
            is_code_line = True
        elif re.match(r'^\s*(try|finally|do)\s*[:\{]', line):
            is_code_line = True
        elif re.match(r'^\s*(else)\s*[:\{]?', line): # else can be bare
             is_code_line = True
        
        # Import/include statements
        if re.match(r'^\s*(import|from\s+\w+\s+import|#include|require|use|package)\s', line):
            is_code_line = True
        
        # Lines ending with code-specific patterns (colons, braces, semicolons)
        if re.search(r'[{};:]\s*$', line):
            is_code_line = True
        
        # Assignment with operators
        if re.search(r'\s*(=|==|!=|<=|>=|\+=|-=|\*=|/=|//=)\s*', line) and re.search(r'[a-z_]\w*\s*(=|\+=)', line, re.IGNORECASE):
            is_code_line = True
        
        # Count the line
        if is_prose and not is_code_line:
            prose_lines += 1
        elif is_code_line and not is_prose:
            code_lines += 1
        elif is_prose and is_code_line:
            # Ambiguous - slight preference for prose if it has prose phrases
            if any(re.search(p, line.lower()) for p in prose_phrases):
                prose_lines += 1
            else:
                code_lines += 1
    
    total_classified = prose_lines + code_lines
    
    # If we classified most lines
    if total_classified >= len(non_empty_lines) * 0.5:
        prose_ratio = prose_lines / max(total_classified, 1)
        
        # If more than 40% are prose, it's likely text with code snippets
        if prose_ratio > 0.4:
            return False
        
        # If more than 60% are code, it's likely code
        if prose_ratio < 0.2:
            return True
    
    # ============================================
    # FALLBACK: STRUCTURAL ANALYSIS
    # ============================================
    
    # Count structural elements
    brace_count = code.count('{') + code.count('}')
    semicolon_count = code.count(';')
    colon_count = len(re.findall(r':\s*$', code, re.MULTILINE))
    
    # Strong structural indicators = definitely code
    if brace_count >= 6 and semicolon_count >= 4:
        return True
    
    # Check for proper indentation blocks (Python-style)
    indented_lines = sum(1 for l in lines if l.startswith('    ') or l.startswith('\t'))
    if indented_lines >= 3 and colon_count >= 2:
        return True
    
    # Check ratio of special characters
    total_chars = len(code.replace(' ', '').replace('\n', ''))
    if total_chars > 0:
        special_chars = len(re.findall(r'[{}\[\]();:=<>!&|+\-*/]', code))
        special_ratio = special_chars / total_chars
        
        # Very high special char ratio with structure
        if special_ratio > 0.10 and (brace_count >= 4 or semicolon_count >= 3):
            return True
    
    # Default: if we couldn't determine, and there's little structure, it's text
    if brace_count < 4 and semicolon_count < 3 and code_lines < 3:
        return False
    
    return code_lines > prose_lines
