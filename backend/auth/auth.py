from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import sqlite3
from db.sqlite_client import get_db_connection

auth_bp = Blueprint("auth", __name__)
JWT_SECRET = "your_super_secret_jwt_key_here"

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed))
        conn.commit()
        
        # Get the new user
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        token = jwt.encode({"sub": str(user['id'])}, JWT_SECRET, algorithm="HS256")
        return jsonify({"token": token, "user": {"id": user['id'], "name": user['name'], "email": user['email']}})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists. Please sign in instead."}), 400
    except Exception as e:
        print("Registration error:", e)
        return jsonify({"error": f"Error occurred: {str(e)}"}), 400

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode(), user['password'].encode('utf-8')):
        token = jwt.encode({"sub": str(user['id'])}, JWT_SECRET, algorithm="HS256")
        return jsonify({"token": token, "user": {"id": user['id'], "name": user['name'], "email": user['email']}})
    
    return jsonify({"error": "Invalid credentials"}), 401
