from ai.llm import get_live_suggestions
from analyzer.complexity_rules import estimate_big_o
from analyzer.pattern_analyzer import PatternAnalyzer
from analyzer.pattern_confidence import PatternConfidence
from analyzer.complexity_map import resolve_complexity


# ==========================================================
# REAL, STATIC, DATA-DRIVEN SCORING LOGIC
# ==========================================================

def complexity_level(static: dict) -> str:
    score = 0
    score += static.get("cyclomaticComplexity", 1)
    score += static.get("maxLoopDepth", 0) * 2
    if static.get("hasRecursion"):
        score += 3
    if static.get("multiRecursion"):
        score += 5

    if score <= 6:
        return "Low"
    if score <= 14:
        return "Medium"
    return "High"


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
# FINAL ANALYSIS PIPELINE
# ==========================================================

def analyze_with_fallback(code: str, static: dict) -> dict:
    pattern = PatternAnalyzer(code, static).detect()

    if pattern and PatternConfidence.is_confident(pattern, code, static):
        time_complexity, space_complexity = resolve_complexity(pattern)
    else:
        time_complexity, space_complexity = estimate_big_o(
            loop_count=static.get("loopCount", 0),
            dynamic_allocations=static.get("dynamicAllocations", 0),
            max_loop_depth=static.get("maxLoopDepth", 0),
            has_log_loop=static.get("hasLogLoop", False),
            has_recursion=static.get("hasRecursion", False),
            multi_recursion=static.get("multiRecursion", False),
        )

    try:
        suggestions = get_live_suggestions(code, static)
    except Exception:
        suggestions = [
            "Reduce unnecessary nested loops.",
            "Avoid repeated computations.",
            "Split large functions into smaller units.",
        ]

    return {
        "language": static.get("language", "Auto"),
        "engine": "Pattern Engine + Rule Engine (STATIC)",
        "metrics": {
            "linesOfCode": static.get("linesOfCode", 0),
            "functionCount": static.get("functionCount", 0),
            "loopCount": static.get("loopCount", 0),
            "conditionalCount": static.get("conditionalCount", 0),
            "cyclomaticComplexity": static.get("cyclomaticComplexity", 1),
        },
        "timeComplexity": time_complexity,
        "spaceComplexity": space_complexity,
        "complexityLevel": complexity_level(static),
        "score": quality_score(static),
        "refactorPercentage": refactor_percentage(static),
        "optimizationPercentage": optimization_percentage(static),
        "suggestions": suggestions,
    }
