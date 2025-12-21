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
You are a senior software engineer.

Based on the following code and its metrics, provide 3 to 5 concise,
actionable suggestions to improve performance, readability, or maintainability.

Metrics:
- Lines of Code: {metrics['linesOfCode']}
- Functions: {metrics['functionCount']}
- Loops: {metrics['loopCount']}
- Conditionals: {metrics['conditionalCount']}
- Cyclomatic Complexity: {metrics['cyclomaticComplexity']}

Code:
{code}

Respond ONLY with a bullet list.
Do not include explanations or introductions.
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
