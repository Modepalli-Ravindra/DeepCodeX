from ai.llm import get_live_suggestions
from analyzer.pattern_analyzer import PatternAnalyzer
from analyzer.pattern_confidence import PatternConfidence
from analyzer.complexity_map import resolve_complexity
from analyzer.per_function_analyzer import analyze_per_function


# ==========================================================
# REAL, STATIC, DATA-DRIVEN SCORING LOGIC
# ==========================================================

def complexity_level_from_worst(worst_time: str) -> str:
    """Get complexity level based on worst-case time."""
    order = {
        "O(1)": 0, "O(log n)": 1, "O(√n)": 2, "O(n)": 3,
        "O(n log n)": 4, "O(n²)": 5, "O(n³)": 6, "O(2ⁿ)": 7, "O(n!)": 8
    }
    level = order.get(worst_time, 3)
    
    if level <= 1:
        return "Low"
    elif level <= 4:
        return "Medium"
    elif level <= 6:
        return "High"
    return "Very High"


def refactor_percentage(static: dict) -> int:
    loc = static.get("linesOfCode", 0)
    funcs = max(static.get("functionCount", 1), 1)
    avg_func_size = loc / funcs

    penalty = 0
    penalty += max(0, avg_func_size - 25) * 0.8
    penalty += static.get("cyclomaticComplexity", 1) * 2
    penalty += static.get("maxLoopDepth", 0) * 5

    if static.get("multiRecursion"):
        penalty += 15
    elif static.get("hasRecursion"):
        penalty += 8

    return min(int(penalty), 100)


def optimization_percentage(static: dict) -> int:
    potential = 0

    potential += static.get("maxLoopDepth", 0) * 10
    potential += static.get("dynamicAllocations", 0) * 5
    potential += static.get("conditionalCount", 0)

    if static.get("multiRecursion"):
        potential += 20
    elif static.get("hasRecursion"):
        potential += 10

    return min(100, potential)


def quality_score(static: dict) -> int:
    base = 100

    base -= static.get("cyclomaticComplexity", 1) * 4
    base -= static.get("maxLoopDepth", 0) * 6
    base -= static.get("dynamicAllocations", 0) * 3

    if static.get("multiRecursion"):
        base -= 15
    elif static.get("hasRecursion"):
        base -= 8

    return max(40, int(base))


# ==========================================================
# FINAL ANALYSIS PIPELINE (HYBRID APPROACH)
# ==========================================================

def analyze_with_fallback(code: str, static: dict) -> dict:
    """
    HYBRID APPROACH:
    1. First try Pattern Recognition (for known algorithms like BFS, binary search)
    2. If pattern found with high confidence, use its known complexity
    3. Otherwise, use per-function analysis for accurate results
    4. Always use MAX (not multiply) for worst-case
    """
    
    # Layer 1: Pattern Recognition (for known algorithms)
    pattern = PatternAnalyzer(code, static).detect()
    
    if pattern and PatternConfidence.is_confident(pattern, code, static):
        # Known algorithm detected - use authoritative complexity
        time_complexity, space_complexity = resolve_complexity(pattern)
        engine = f"Pattern Engine: {pattern}"
        per_func_result = None
    else:
        # Layer 2: Per-function analysis (correct approach for multi-function code)
        per_func_result = analyze_per_function(code)
        time_complexity = per_func_result.get("worstTime", "O(n)")
        space_complexity = per_func_result.get("worstSpace", "O(1)")
        engine = "Per-Function Analyzer"
    
    # Get complexity level from worst-case
    level = complexity_level_from_worst(time_complexity)
    
    # Get suggestions
    try:
        suggestions = get_live_suggestions(code, static)
    except Exception:
        suggestions = [
            "Reduce unnecessary nested loops.",
            "Avoid repeated computations.",
            "Split large functions into smaller units.",
        ]

    # Build result
    result = {
        "language": static.get("language", "Auto"),
        "engine": engine,
        "metrics": {
            "linesOfCode": static.get("linesOfCode", 0),
            "functionCount": static.get("functionCount", 1),
            "loopCount": static.get("loopCount", 0),
            "conditionalCount": static.get("conditionalCount", 0),
            "cyclomaticComplexity": static.get("cyclomaticComplexity", 1),
        },
        
        # Worst-case complexity
        "timeComplexity": time_complexity,
        "spaceComplexity": space_complexity,
        
        "complexityLevel": level,
        "score": quality_score(static),
        "refactorPercentage": refactor_percentage(static),
        "optimizationPercentage": optimization_percentage(static),
        "suggestions": suggestions,
    }
    
    # Add per-function breakdown if available
    if per_func_result:
        result["worstTimeFunction"] = per_func_result.get("worstTimeFunction", "main")
        result["worstSpaceFunction"] = per_func_result.get("worstSpaceFunction", "main")
        result["perFunctionAnalysis"] = per_func_result.get("functions", [])
        result["summary"] = per_func_result.get("summary", "")
    
    return result
