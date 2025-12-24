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

from db.supabase_client import supabase
import hashlib
import jwt
import os

app = Flask(__name__)
# Allow * allows any origin, including localhost and 192.168.x.x
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "OPTIONS"])

app.register_blueprint(auth_bp, url_prefix="/auth")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

# Initialize JWK Client for Supabase (Handling ES256/RS256)
jwks_url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
jwk_client = jwt.PyJWKClient(jwks_url)

def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()

def get_user_id_from_request():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, "Missing or invalid Authorization header"

    token = auth_header.replace("Bearer ", "")
    try:
        # 1. Try verifying with Supabase JWKS (Handles ES256/RS256)
        try:
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["HS256", "ES256", "RS256"],
                audience="authenticated",
            )
            return payload.get("sub"), None
        except Exception as jwk_err:
            # 2. Fallback to HS256 with shared secret (Legacy/Alternative)
            try:
                payload = jwt.decode(
                    token,
                    SUPABASE_JWT_SECRET,
                    algorithms=["HS256"],
                    audience="authenticated",
                )
                return payload.get("sub"), None
            except Exception as hs_err:
                return None, f"Auth Error: {str(jwk_err)}"
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
            supabase.table("analysis_history").insert({
                "user_id": user_id,  # 🔐 REQUIRED
                "language": final_result.get("language"),
                "code_hash": hash_code(code),
                "time_complexity": final_result.get("timeComplexity"),
                "space_complexity": final_result.get("spaceComplexity"),
                "cyclomatic": final_result.get("cyclomaticComplexity"),
                "optimization_score": final_result.get("optimizationPercentage"),
                "functions": static_result.get("functionCount"),
                "loops": static_result.get("loopCount"),
                "conditions": static_result.get("conditionalCount"),
                "lines": static_result.get("linesOfCode"),
                "ai_suggestions": "\n".join(final_result.get("suggestions", [])),
            }).execute()
        except Exception as e:
            print("Supabase insert failed:", e)

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
        response = (
            supabase
            .table("analysis_history")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        return jsonify(response.data)
    except Exception as e:
        print("Supabase history fetch failed:", e)
        return jsonify([])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
