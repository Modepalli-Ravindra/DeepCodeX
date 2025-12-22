from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS

from analyzer.static_analyzer import analyze_static
from analyzer.fallback import analyze_with_fallback
from analyzer.language_router import detect_language
from auth.auth import auth_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(auth_bp, url_prefix="/auth")


@app.route("/analyze", methods=["POST"])
def analyze_code():
    data = request.json
    code = data.get("code", "")

    if not code.strip():
        return jsonify({"error": "Empty code"}), 400

    # ---------- LANGUAGE DETECTION ----------
    language = detect_language(code)

    # ---------- CHECK FOR PLAIN TEXT (NO CODE) ----------
    if language == "Plain Text":
        return jsonify({
            "language": "Plain Text",
            "isCode": False,
            "engine": "None",
            "message": "No code detected. Please paste valid source code.",
            "metrics": {
                "linesOfCode": len(code.strip().split('\n')),
                "functionCount": 0,
                "loopCount": 0,
                "conditionalCount": 0,
                "cyclomaticComplexity": 0,
            },
            "timeComplexity": "N/A",
            "spaceComplexity": "N/A",
            "complexityLevel": "None",
            "score": 0,
            "refactorPercentage": 0,
            "optimizationPercentage": 0,
            "suggestions": [
                "The input appears to be plain text, not code.",
                "Please paste source code in a supported language:",
                "Python, Java, C++, C, JavaScript, TypeScript, Go, Rust, Ruby, or PHP."
            ],
        })

    # ---------- STATIC ANALYSIS (RULE-BASED) ----------
    static_result = analyze_static(code, language)
    
    # Override language with our enhanced detection
    static_result["language"] = language

    # ---------- FINAL PIPELINE ----------
    final_result = analyze_with_fallback(code, static_result)
    
    # Ensure language is set correctly in final result
    final_result["language"] = language
    final_result["isCode"] = True

    return jsonify(final_result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
