"""
app.py — Main Flask Application (Entry Point)
==============================================
How to run locally (XAMPP):
  1. Start XAMPP → start Apache + MySQL
  2. Open phpMyAdmin → create database 'prodify_db'
  3. Run: python app.py
  4. Open: http://localhost:5000

How to deploy on PythonAnywhere:
  1. Upload this backend folder
  2. Update DB_CONFIG in db.py with your PA credentials
  3. Create a Web App pointing to this app.py
  4. WSGI file should import 'app' from this file
"""

from flask import Flask, send_from_directory
from flask_cors import CORS

from db import init_db
from routes.auth      import auth_bp
from routes.tasks     import tasks_bp
from routes.habits    import habits_bp
from routes.dashboard import dashboard_bp


# ── Create the Flask app ──────────────────────────────────────
# static_folder points to the frontend folder (one level up from backend)
app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path=""
)

# Secret key is required for Flask sessions (login state)
# IMPORTANT: Change this to a long random string before going live!
app.secret_key = "prodify_secret_key_change_in_production_2024"

# Session cookie settings
app.config["SESSION_COOKIE_HTTPONLY"] = True   # Prevents JS from reading the cookie
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"   # Required: cross-origin (Live Server port != Flask port)
app.config["SESSION_COOKIE_SECURE"]   = False     # Must be False on HTTP localhost
app.secret_key = "your_secret_key_123"
CORS(app, supports_credentials=True) 

# Allow the frontend (same origin) to send cookies with API requests
CORS(app, supports_credentials=True)

# ── Register route blueprints ─────────────────────────────────
# Each blueprint is a separate module that handles one feature area
app.register_blueprint(auth_bp)       # /register, /login, /logout
app.register_blueprint(tasks_bp)      # /tasks, /tasks/<id>
app.register_blueprint(habits_bp)     # /habits, /habits/complete, /habits/<id>
app.register_blueprint(dashboard_bp)  # /dashboard-stats


# ── Serve frontend HTML files ─────────────────────────────────

@app.route("/")
def serve_landing():
    """Serve the main landing page."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    """Serve all other frontend files (CSS, JS, HTML pages)."""
    return send_from_directory(app.static_folder, filename)


# ── Start the server ──────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  PRODIFY Backend Starting...")
    print("=" * 50)

    init_db()  # Create DB tables if they don't exist yet

    print("  Server running at: http://localhost:5000")
    print("=" * 50)

    app.run(debug=True, host="0.0.0.0", port=5000)
