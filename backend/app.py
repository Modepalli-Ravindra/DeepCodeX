from dotenv import load_dotenv
import os

# Load from current directory, then parent directory
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Fallback for OpenRouter Key if not in .env (Restored from history)
if not os.getenv("OPENROUTER_API_KEY"):
    os.environ["OPENROUTER_API_KEY"] = "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"

from flask import Flask, request, jsonify
from flask_cors import CORS

from analyzer.static_analyzer import analyze_static
from analyzer.fallback import analyze_with_fallback
from analyzer.language_router import detect_language
from auth.auth import auth_bp

import hashlib
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS"])

app.register_blueprint(auth_bp, url_prefix="/auth")

def get_db_connection():
    conn = sqlite3.connect('history.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            language TEXT,
            code_hash TEXT,
            time_complexity TEXT,
            space_complexity TEXT,
            cyclomatic TEXT,
            optimization_score REAL,
            functions INTEGER,
            loops INTEGER,
            conditions INTEGER,
            lines INTEGER,
            ai_suggestions TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()

import jwt

JWT_SECRET = "your_super_secret_jwt_key_here"

def get_user_id_from_request():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, "Missing or invalid Authorization header"

    token = auth_header.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("sub"), None
    except Exception as e:
        return None, f"Auth Error: {str(e)}"


@app.route("/analyze", methods=["POST"])
def analyze_code():
    data = request.json
    code = data.get("code", "")

    if not code.strip():
        return jsonify({"error": "Empty code"}), 400

    user_id, auth_error = get_user_id_from_request()
    if not user_id:
        return jsonify({"error": auth_error}), 401

    language = detect_language(code)

    if language == "Plain Text":
        return jsonify({
            "language": "Plain Text",
            "isCode": False,
            "engine": "None",
            "message": "No code detected.",
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
            "suggestions": [],
        })

    try:
        static_result = analyze_static(code, language)
        static_result["language"] = language

        final_result = analyze_with_fallback(code, static_result)
        final_result["language"] = language
        final_result["isCode"] = True

        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO analysis_history (user_id, language, code_hash, time_complexity, space_complexity, cyclomatic, optimization_score, functions, loops, conditions, lines, ai_suggestions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                final_result.get("language"),
                hash_code(code),
                final_result.get("timeComplexity"),
                final_result.get("spaceComplexity"),
                final_result.get("cyclomaticComplexity"),
                final_result.get("optimizationPercentage"),
                static_result.get("functionCount"),
                static_result.get("loopCount"),
                static_result.get("conditionalCount"),
                static_result.get("linesOfCode"),
                "\n".join(final_result.get("suggestions", []))
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print("SQLite insert failed:", e)

        return jsonify(final_result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal Analysis Error: {str(e)}"}), 500


@app.route("/history", methods=["GET"])
def get_history():
    user_id, auth_error = get_user_id_from_request()
    if not user_id:
        return jsonify({"error": auth_error}), 401

    try:
        conn = get_db_connection()
        rows = conn.execute(
            'SELECT * FROM analysis_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 50',
            (user_id,)
        ).fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        print("SQLite history fetch failed:", e)
        return jsonify([])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
