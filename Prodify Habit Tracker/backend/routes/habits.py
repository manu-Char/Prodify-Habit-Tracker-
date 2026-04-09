"""
habits.py — Habit Tracker Routes
===================================
Handles all habit-related operations.

Routes:
  GET    /habits            → Get all habits for the logged-in user (with today's status)
  POST   /habits            → Create a new habit
  POST   /habits/complete   → Mark a habit as done for today
  DELETE /habits/<id>       → Delete a habit and all its logs

Core rule — one completion per day:
  Each habit can only be marked complete once per calendar day.
  This is enforced by checking if a row exists in habit_logs for today's date.
  The DB also has a UNIQUE constraint on (habit_id, completion_date) as a safety net.
"""

from flask import Blueprint, request, jsonify, session
from datetime import date
from db import get_connection

habits_bp = Blueprint("habits", __name__)


def get_user_id():
    """Returns the logged-in user's ID from session, or None if not logged in."""
    return session.get("user_id")


@habits_bp.route("/habits", methods=["GET"])
def get_habits():
    """
    Returns all habits for the logged-in user.
    Each habit includes a 'completed_today' boolean field so the
    frontend knows whether to show the "Mark Done" button or "Done Today" chip.
    """
    user_id = get_user_id()
    if not user_id:
        return jsonify({"status": "error", "message": "Please log in to view habits"}), 401

    today  = date.today()
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get all habits for this user
    cursor.execute(
        "SELECT id, habit_name, created_date FROM habits WHERE user_id = %s ORDER BY created_date DESC",
        (user_id,)
    )
    habits = cursor.fetchall()

    # For each habit, check if it was already completed today
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

    return jsonify({"status": "success", "habits": habits}), 200


@habits_bp.route("/habits", methods=["POST"])
def create_habit():
    """
    Create a new habit for the logged-in user.
    Expects JSON body: { "habit_name": "..." }
    """
    user_id = get_user_id()
    if not user_id:
        return jsonify({"status": "error", "message": "Please log in to create habits"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    habit_name = data.get("habit_name", "").strip()
    if not habit_name:
        return jsonify({"status": "error", "message": "Habit name is required"}), 400

    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO habits (user_id, habit_name) VALUES (%s, %s)",
        (user_id, habit_name)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"status": "success", "message": "Habit created", "habit_id": new_id}), 201


@habits_bp.route("/habits/complete", methods=["POST"])
def complete_habit():
    """
    Mark a habit as completed for today.
    Expects JSON body: { "habit_id": 123 }

    Rule: Only ONE completion per habit per calendar day.
    Returns an error if the habit was already completed today.
    """
    user_id = get_user_id()
    if not user_id:
        return jsonify({"status": "error", "message": "Please log in"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    habit_id = data.get("habit_id")
    if not habit_id:
        return jsonify({"status": "error", "message": "habit_id is required"}), 400

    today  = date.today()
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Make sure this habit belongs to the logged-in user
    cursor.execute(
        "SELECT id FROM habits WHERE id = %s AND user_id = %s",
        (habit_id, user_id)
    )
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "Habit not found"}), 404

    # Check if already completed today
    cursor.execute(
        "SELECT id FROM habit_logs WHERE habit_id = %s AND completion_date = %s",
        (habit_id, today)
    )
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "This habit is already completed for today"}), 400

    # Insert a completion log for today
    cursor.execute(
        "INSERT INTO habit_logs (habit_id, completion_date) VALUES (%s, %s)",
        (habit_id, today)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "success", "message": "Habit marked as completed for today"}), 201


@habits_bp.route("/habits/<int:habit_id>", methods=["DELETE"])
def delete_habit(habit_id):
    """
    Delete a habit.
    All associated habit_logs rows are also deleted automatically
    because the DB table uses ON DELETE CASCADE.
    Only the habit's owner can delete it.
    """
    user_id = get_user_id()
    if not user_id:
        return jsonify({"status": "error", "message": "Please log in"}), 401

    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Verify ownership before deleting
    cursor.execute(
        "SELECT id FROM habits WHERE id = %s AND user_id = %s",
        (habit_id, user_id)
    )
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "Habit not found"}), 404

    cursor.execute("DELETE FROM habits WHERE id = %s", (habit_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "success", "message": "Habit deleted"}), 200
