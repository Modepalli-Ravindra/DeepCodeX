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
    garbage = ["<s>", "</s>", "[INST]", "[/INST]", "[OUT]", "System:", "AI:", "Output:"]
    for line in content.splitlines():
        line = line.strip()
        if not line: continue
        for token in garbage: line = line.replace(token, "")
        line = line.strip().lstrip("-•*0123456789. ").strip()
        if len(line) > 10: suggestions.append(line)

    if not suggestions:
        raise RuntimeError("No valid suggestions generated")

    return suggestions[:5]


def analyze_complexity_with_llm(code: str) -> dict:
    """
    Performs a deep Chain-of-Thought analysis using the LLM to determine
    accurate Time and Space complexity.
    Returns a dict with keys: 'time', 'space', 'reasoning'.
    """
    if not OPENROUTER_API_KEY:
        return None

    prompt = f"""
You are an elite algorithm complexity expert. Your goal is to provide 100% accurate Big-O analysis used by top-tier tech companies.

Analyze the following code using a strict CHAIN OF THOUGHT process:
1. ALGORITHM ID: Identify the specific algorithm (e.g., Merge Sort, BFS, DP with Memoization).
2. KEY OPERATIONS: Identify the loops, recursion depths, and dominant operations.
3. INPUT SCALING: How do these operations grow as input 'N' increases?
4. WORST CASE: Consider the worst-case scenario (e.g., quicksort pivot selection, hash collisions).
5. INTRINSIC COMPLEXITY PRIORITY:
   - If a function `solve(n)` is O(n), but called as `solve(5)`, report O(n) (the algorithmic complexity).
   - Only report O(1) if the algorithm ITSELF is constant time regardless of input.
   - For recursive functions (e.g. Fibonacci), report the complexity of the recursion relation (e.g. O(2^n)), NOT the runtime of a specific call.
6. SPACE ANALYSIS: Include stack depth for recursion and auxiliary memory.

CODE:
{code}

You must output valid JSON ONLY. No other text.
Format:
{{
  "time_complexity": "O(...)",
  "space_complexity": "O(...)",
  "reasoning": "Brief summary of the chain-of-thought analysis (max 2 sentences)."
}}
"""

    try:
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
                "temperature": 0.2, # Low temperature for precision
                "response_format": { "type": "json_object" } 
            },
            timeout=20,
        )

        if response.status_code != 200:
            return None

        data = response.json()
        if "choices" not in data or not data["choices"]:
            return None

        import json
        content = data["choices"][0]["message"]["content"]
        # Sanitize markdown code blocks if present
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        
        return json.loads(content)

    except Exception as e:
        print(f"LLM Analysis failed: {e}")
        return None
