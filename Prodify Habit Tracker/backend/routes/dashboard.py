"""
dashboard.py — Dashboard Statistics Route
==========================================
Returns all data needed by the dashboard page in a single API call.

Route:
  GET /dashboard-stats

Response structure:
  {
    "status": "success",
    "stats": {
      "total_tasks":     <int>,   -- all tasks ever created
      "completed_tasks": <int>,   -- tasks marked as done
      "pending_tasks":   <int>,   -- tasks not yet done
      "total_habits":    <int>,   -- habits being tracked
      "habits_today":    <int>    -- habits completed today
    },
    "latest_tasks":    [...],  -- last 5 tasks created
    "habits_overview": [...]   -- all habits with completed_today flag
  }
"""

from flask import Blueprint, jsonify, session
from datetime import date
from db import get_connection

dashboard_bp = Blueprint("dashboard", __name__)


def get_user_id():
    """Returns the logged-in user's ID from session, or None if not logged in."""
    return session.get("user_id")


@dashboard_bp.route("/dashboard-stats", methods=["GET"])
def dashboard_stats():
    """
    Returns all stats and previews needed for the dashboard page.
    Combines task counts, habit counts, latest tasks, and habits overview
    into one response — so the frontend only needs to make one API call.
    """
    user_id = get_user_id()
    if not user_id:
        return jsonify({"status": "error", "message": "Please log in"}), 401

    today  = date.today()
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ── Task counts ───────────────────────────────────────────
    cursor.execute("SELECT COUNT(*) AS total FROM tasks WHERE user_id = %s", (user_id,))
    total_tasks = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) AS total FROM tasks WHERE user_id = %s AND status = 'completed'",
        (user_id,)
    )
    completed_tasks = cursor.fetchone()["total"]
    pending_tasks   = total_tasks - completed_tasks

    # ── Habit counts ──────────────────────────────────────────
    cursor.execute("SELECT COUNT(*) AS total FROM habits WHERE user_id = %s", (user_id,))
    total_habits = cursor.fetchone()["total"]

    # Count habits that have a completion log for today
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM habit_logs hl
        JOIN habits h ON h.id = hl.habit_id
        WHERE h.user_id = %s AND hl.completion_date = %s
        """,
        (user_id, today)
    )
    habits_today = cursor.fetchone()["total"]

    # ── Latest 5 tasks ────────────────────────────────────────
    cursor.execute(
        """
        SELECT id, title, description, status, created_date
        FROM tasks
        WHERE user_id = %s
        ORDER BY created_date DESC
        LIMIT 5
        """,
        (user_id,)
    )
    latest_tasks = cursor.fetchall()
    for task in latest_tasks:
        if task["created_date"]:
            task["created_date"] = str(task["created_date"])

    # ── All habits with today's completion status ─────────────
    cursor.execute(
        "SELECT id, habit_name, created_date FROM habits WHERE user_id = %s ORDER BY created_date DESC",
        (user_id,)
    )
    habits = cursor.fetchall()
    for habit in habits:
        cursor.execute(
            "SELECT id FROM habit_logs WHERE habit_id = %s AND completion_date = %s",
            (habit["id"], today)
        )
        habit["completed_today"] = bool(cursor.fetchone())
        if habit["created_date"]:
            habit["created_date"] = str(habit["created_date"])

    cursor.close()
    conn.close()

    return jsonify({
        "status": "success",
        "stats": {
            "total_tasks":     total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks":   pending_tasks,
            "total_habits":    total_habits,
            "habits_today":    habits_today,
        },
        "latest_tasks":    latest_tasks,
        "habits_overview": habits,
    }), 200
