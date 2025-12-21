from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS

from analyzer.static_analyzer import analyze_static
from analyzer.fallback import analyze_with_fallback
from analyzer.language_router import detect_language
from auth.auth import auth_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix="/auth")


@app.route("/analyze", methods=["POST"])
def analyze_code():
    data = request.json
    code = data.get("code", "")

    if not code.strip():
        return jsonify({"error": "Empty code"}), 400

    # ---------- LANGUAGE DETECTION ----------
    language = detect_language(code)

    # ---------- STATIC ANALYSIS (RULE-BASED) ----------
    static_result = analyze_static(code, language)

    # ---------- FINAL PIPELINE ----------
    final_result = analyze_with_fallback(code, static_result)

    return jsonify(final_result)


if __name__ == "__main__":
    app.run(debug=True)
