# ==========================================================
# LANGUAGE DETECTION (DETERMINISTIC, NO AI)
# ==========================================================

def detect_language(code: str) -> str:
    """
    Very lightweight heuristic-based language detection.
    Used ONLY to route analysis logic.
    """

    code_lower = code.lower()

    # ---------- PYTHON ----------
    if "def " in code_lower or "elif " in code_lower or "import " in code_lower:
        return "python"

    # ---------- JAVA ----------
    if "public class" in code_lower or "system.out.println" in code_lower:
        return "java"

    # ---------- C / C++ ----------
    if "#include <" in code_lower or "printf(" in code_lower:
        return "cpp"

    # ---------- JAVASCRIPT / TYPESCRIPT ----------
    if "function " in code_lower or "=>" in code_lower:
        return "javascript"

    return "generic"
