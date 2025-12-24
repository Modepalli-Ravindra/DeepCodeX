from ai.llm import get_live_suggestions, analyze_complexity_with_llm
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
    """Realistic optimization potential (max 40-50% for typical code)."""
    potential = 0

    # High complexity / depth suggests *some* overhead, but not 100%
    potential += min(15, static.get("maxLoopDepth", 0) * 3)
    potential += min(10, static.get("dynamicAllocations", 0) * 1)
    
    if static.get("multiRecursion"):
        potential += 10
    elif static.get("hasRecursion"):
        potential += 5

    # Cap at 45% to reflect that core algorithms (sorting, DP) are often essential
    return min(45, potential)


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
    
    # LEVEL 0: AI Deep Analysis (Tricks & Logics from Advanced LLMs)
    # The user requested "Genei/ChatGPT" level accuracy, so we prioritize the LLM if available.
    ai_result = analyze_complexity_with_llm(code)
    
    if ai_result:
        print(f"DEBUG: Using LLM Result: {ai_result}")
        final_time = ai_result.get("time_complexity", "O(n)")
        final_space = ai_result.get("space_complexity", "O(1)")
        reasoning = ai_result.get("reasoning", "AI-Powered Analysis")
        
        # Determine level for the AI result
        level = complexity_level_from_worst(final_time)
        
         # Get suggestions (reused logic)
        try:
            suggestions = get_live_suggestions(code, static)
        except Exception:
            suggestions = ["Optimize logic based on AI findings."]

        return {
            "language": static.get("language", "Auto"),
            "engine": "DeepCodeX Advanced Engine",
            "metrics": {
                "linesOfCode": static.get("linesOfCode", 0),
                "functionCount": static.get("functionCount", 1),
                "loopCount": static.get("loopCount", 0),
                "conditionalCount": static.get("conditionalCount", 0),
            },
            "timeComplexity": final_time,
            "spaceComplexity": final_space,
            "complexityLevel": level,
            "score": quality_score(static), # Keep static quality score
            "refactorPercentage": refactor_percentage(static),
            "optimizationPercentage": optimization_percentage(static),
            "suggestions": suggestions,
            "summary": reasoning,
            "worstTimeFunction": "Global Analysis",
            "worstSpaceFunction": "Global Analysis",
        }

    # Layer 2: Per-function analysis (CORE STRUCTURAL ANALYSIS)
    per_func_result = analyze_per_function(code)
    
    final_time = per_func_result.get("worstTime", "O(n)")
    final_space = per_func_result.get("worstSpace", "O(1)")
    found_pattern_name = None
    
    # Layer 1: Pattern Recognition (RECOGNITION OVERRIDE)
    pattern = PatternAnalyzer(code, static).detect()
    
    # COMPLEXITY ORDERING (Internal helper)
    ORDER = {
        "O(1)": 0, "O(log n)": 1, "O(√n)": 2, "O(n)": 3, "O(V + E)": 3,
        "O(n log n)": 4, "O(E log V)": 4, "O(n²)": 5, "O(V²)": 5, "O(n³)": 6, 
        "O(2ⁿ)": 7, "O(n!)": 8
    }
    
    if pattern and PatternConfidence.is_confident(pattern, code, static):
        p_time, p_space = resolve_complexity(pattern)
        # DOMINANCE RULE: Final complexity = MAX(Logic, Pattern)
        if ORDER.get(p_time, 0) > ORDER.get(final_time, 0):
            # Gate: Pattern cannot elevate O(1) demos to O(n!/2ⁿ) unless logic agrees it's scaling
            if p_time in ["O(2ⁿ)", "O(n!)"] and final_time not in ["O(2ⁿ)", "O(n!)"]:
                pass
            else:
                final_time = p_time
                final_space = p_space
                found_pattern_name = pattern
    
    # Get complexity level from final consensus
    level = complexity_level_from_worst(final_time)
    
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
        "engine": f"Hybrid Static Analyzer (Pattern: {found_pattern_name})" if found_pattern_name else "Per-Function Logic Engine",
        "metrics": {
            "linesOfCode": static.get("linesOfCode", 0),
            "functionCount": static.get("functionCount", 1),
            "loopCount": static.get("loopCount", 0),
            "conditionalCount": static.get("conditionalCount", 0),
        },
        
        # Worst-case complexity
        "timeComplexity": final_time,
        "spaceComplexity": final_space,
        
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
