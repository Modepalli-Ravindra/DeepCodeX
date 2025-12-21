from flask import Blueprint, request, jsonify
import bcrypt

auth_bp = Blueprint("auth", __name__)

users = {}

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data["email"]
    password = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())
    users[email] = password
    return jsonify({"message": "Registered successfully"})

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"].encode()

    if email in users and bcrypt.checkpw(password, users[email]):
        return jsonify({"message": "Login success"})
    return jsonify({"error": "Invalid credentials"}), 401
