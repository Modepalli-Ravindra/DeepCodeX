import requests
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "mistralai/mistral-7b-instruct"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


from typing import List

def get_live_suggestions(code: str, metrics: dict) -> List[str]:
    """
    Returns 3–5 live, LLM-generated improvement suggestions.
    Guaranteed to return a clean list or raise an exception.
    """

    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    prompt = f"""
You are a senior software engineer and complexity analysis expert.

When providing suggestions, follow these 4 fundamental bases for complexity analysis:
1. Control-Flow Growth (Loops): 
   - for i=0 to n -> O(n)
   - Nested loops -> multiply (2 loops = O(n²), 3 loops = O(n³))
   - i *= 2 or i /= 2 -> O(log n)
2. Recursion Pattern:
   - f(n-1) -> O(n)
   - f(n/2) -> O(log n)
   - f(n-1) + f(n-2) -> O(2ⁿ)
   - Subsets -> O(2ⁿ)
   - Permutations -> O(n!)
3. Data Structure Size (Space Complexity):
   - Array size n -> O(n)
   - Matrix n x n -> O(n²)
   - DP table n x m -> O(nm)
   - Recursion stack -> depth of recursion
4. Dominance Rule:
   - Take the maximum growth across multiple algorithms (e.g., Sorting O(n²) + Backtracking O(n!) -> O(n!)).

5. Constant Bound Rule (CRITICAL):
   - If a function is called with a literal constant (e.g., fib(20), nQueens(8), backtracking("ABC")), its EFFECTIVE complexity at that call site is O(1).
   - Do NOT suggest optimizations for O(1) bounded calls. Focus on scaling variables.

6. Algorithmic Intent & Honest Claims:
   - Do NOT suggest replacing core algorithms (Sorting, Graph Traversals, DP) with standard library functions (e.g., do not suggest Arrays.sort() to replace QuickSort).
   - Be HONEST about optimization limits. Pruning in Backtracking does NOT reduce O(2ⁿ) to O(n); it only improves the average case. Do NOT claim O(n) for exponential problems.
   - Respect Space Complexity limits. DP tables like LPS or LCS require O(n²) space. Do NOT suggest O(1) space if the algorithm fundamentally requires a table.

7. No Placeholders:
   - Provide concrete suggestions based on the specific variables and logic found in the code.

Based on the following code and its metrics, provide 3 to 5 concise, actionable, and THEORETICALLY ACCURATE suggestions to improve performance, readability, or maintainability.

Metrics:
- Lines of Code: {metrics['linesOfCode']}
- Functions: {metrics['functionCount']}
- Loops: {metrics['loopCount']}
- Conditionals: {metrics['conditionalCount']}
- Cyclomatic Complexity: {metrics['cyclomaticComplexity']}

Code:
{code}

Respond ONLY with a bullet list of accurate suggestions.
Do not include explanations, introductions, or over-promises.
"""

    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4,
        },
        timeout=15,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter error {response.status_code}: {response.text}"
        )

    data = response.json()

    if "choices" not in data or not data["choices"]:
        raise RuntimeError("Invalid OpenRouter response format")

    content = data["choices"][0]["message"]["content"]

    # ---- SANITIZE OUTPUT ----
    suggestions = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue

        # Remove bullets, numbering, dashes
        line = line.lstrip("-•*0123456789. ").strip()

        if len(line) > 5:
            suggestions.append(line)

    if not suggestions:
        raise RuntimeError("No valid suggestions generated")

    return suggestions[:5]
