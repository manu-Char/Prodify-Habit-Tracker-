"""
auth.py — Authentication Routes
=================================
Handles user registration, login, and logout.

Routes:
  POST /register  → Create a new user account
  POST /login     → Log in and start a session
  GET  /logout    → Clear session and log out

How sessions work:
  After a successful login, Flask stores the user's ID and username
  in a server-side session cookie. All protected routes check this
  session to verify the user is logged in.
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user account.

    Expects JSON body: { "username": "...", "email": "...", "password": "..." }

    Steps:
      1. Validate that all fields are present
      2. Check the email is not already registered
      3. Hash the password (never store plain text)
      4. Insert the new user into the database
    """
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    # Extract and clean inputs
    username = data.get("username", "").strip()
    email    = data.get("email",    "").strip().lower()
    password = data.get("password", "").strip()

    # Basic validation
    if not username or not email or not password:
        return jsonify({"status": "error", "message": "All fields are required"}), 400

    if len(password) < 6:
        return jsonify({"status": "error", "message": "Password must be at least 6 characters"}), 400

    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if this email is already taken
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "An account with this email already exists"}), 409

    # Hash password and save new user
    hashed_password = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
        (username, email, hashed_password)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "success", "message": "Account created successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Log in an existing user.

    Expects JSON body: { "email": "...", "password": "..." }

    On success:
      - Stores user_id and username in the Flask session
      - Returns the username so the frontend can store it in localStorage
    """
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    email    = data.get("email",    "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"}), 400

    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Look up the user by email
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    # Verify the password matches the stored hash
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    # Save user info to session — this is what keeps the user "logged in"
    session["user_id"]  = user["id"]
    session["username"] = user["username"]

    return jsonify({
        "status":   "success",
        "message":  "Logged in successfully",
        "username": user["username"]
    }), 200


@auth_bp.route("/logout", methods=["GET"])
def logout():
    """
    Log out by clearing the session.
    The user's login state is removed — they must log in again to access protected routes.
    """
    session.clear()
    return jsonify({"status": "success", "message": "Logged out"}), 200
