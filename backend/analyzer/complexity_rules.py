# ==========================================================
# COMPLEXITY RULES ENGINE (FALLBACK)
# Used when no specific pattern is detected
# ==========================================================

def estimate_big_o(
    loop_count: int,
    dynamic_allocations: int,
    max_loop_depth: int,
    has_log_loop: bool = False,
    has_recursion: bool = False,
    multi_recursion: bool = False,
):
    """
    Estimate time and space complexity based on static metrics.
    This is the fallback when pattern matching doesn't apply.
    """
    
    # ---------- TIME COMPLEXITY ----------
    
    # Exponential recursion (e.g., naive Fibonacci, subset sum)
    if multi_recursion:
        time_complexity = "O(2ⁿ)"

    # Logarithmic with recursion (e.g., binary search recursive)
    elif has_recursion and has_log_loop:
        time_complexity = "O(log n)"

    # Linear recursion (e.g., factorial, linear traversal)
    elif has_recursion and max_loop_depth == 0:
        time_complexity = "O(n)"

    # Recursion with loops (e.g., merge sort pattern)
    elif has_recursion and max_loop_depth >= 1:
        time_complexity = "O(n log n)"

    # Pure logarithmic (e.g., binary search iterative)
    elif has_log_loop and max_loop_depth <= 1:
        time_complexity = "O(log n)"

    # No loops at all - constant time
    elif max_loop_depth == 0 and loop_count == 0:
        time_complexity = "O(1)"

    # Single loop - linear time
    elif max_loop_depth == 1:
        time_complexity = "O(n)"

    # Nested loops - polynomial time
    elif max_loop_depth == 2:
        time_complexity = "O(n²)"

    elif max_loop_depth == 3:
        time_complexity = "O(n³)"

    else:
        time_complexity = f"O(n^{max_loop_depth})"

    # ---------- SPACE COMPLEXITY ----------

    # Multi-recursion typically needs O(n) stack space
    if multi_recursion:
        space_complexity = "O(n)"

    # Single recursion also uses stack space
    elif has_recursion:
        if has_log_loop:
            space_complexity = "O(log n)"
        else:
            space_complexity = "O(n)"

    # Logarithmic with dynamic allocations
    elif has_log_loop and dynamic_allocations > 0:
        space_complexity = "O(log n)"

    # Dynamic allocations suggest growing data structures
    elif dynamic_allocations > 0:
        space_complexity = "O(n)"

    # No dynamic allocations - constant space
    else:
        space_complexity = "O(1)"

    return time_complexity, space_complexity
