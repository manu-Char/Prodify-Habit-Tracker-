"""
tasks.py — Task Management Routes
====================================
Handles all CRUD operations for tasks.

Routes:
  GET    /tasks          → Get all tasks for the logged-in user
  POST   /tasks          → Create a new task
  PUT    /tasks/<id>     → Mark a task as completed
  DELETE /tasks/<id>     → Delete a task

All routes require the user to be logged in.
Login state is checked using the Flask session (set during /login).
"""

from flask import Blueprint, request, jsonify, session
from db import get_connection

tasks_bp = Blueprint("tasks", __name__)


def get_user_id():
    """
    Returns the logged-in user's ID from the session.
    Returns None if the user is not logged in.
    All routes call this first to check authentication.
    """
    return session.get("user_id")


@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    """
    Returns all tasks belonging to the logged-in user.
    Tasks are ordered newest first.

    Response includes: id, title, description, status, created_date, completed_date
    """
    user_id = get_user_id()
    if not user_id:
        return jsonify({"status": "error", "message": "Please log in to view tasks"}), 401

    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, title, description, status, created_date, completed_date
        FROM tasks
        WHERE user_id = %s
        ORDER BY created_date DESC
        """,
        (user_id,)
    )
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert datetime objects to strings so they can be sent as JSON
    for task in tasks:
        if task["created_date"]:
            task["created_date"] = str(task["created_date"])
        if task["completed_date"]:
            task["completed_date"] = str(task["completed_date"])

    return jsonify({"status": "success", "tasks": tasks}), 200


@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    """
    Create a new task for the logged-in user.

    Expects JSON body: { "title": "...", "description": "..." (optional) }

    Returns the new task's ID so the frontend can reference it.
    """
    user_id = get_user_id()
    if not user_id:
        return jsonify({"status": "error", "message": "Please log in to create tasks"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    title       = data.get("title",       "").strip()
    description = data.get("description", "").strip()

    if not title:
        return jsonify({"status": "error", "message": "Task title is required"}), 400

    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (user_id, title, description) VALUES (%s, %s, %s)",
        (user_id, title, description or None)
    )
    conn.commit()
    new_id = cursor.lastrowid  # Get the ID of the newly inserted row
    cursor.close()
    conn.close()

    return jsonify({"status": "success", "message": "Task created", "task_id": new_id}), 201


@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def complete_task(task_id):
    """
    Mark a task as completed.

    Expects JSON body: { "status": "completed" }

    Safety checks:
      - Task must exist and belong to this user
      - Task must not already be completed
    """
    user_id = get_user_id()
    if not user_id:
        return jsonify({"status": "error", "message": "Please log in"}), 401

    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Verify the task exists and belongs to this user
    cursor.execute(
        "SELECT id, status FROM tasks WHERE id = %s AND user_id = %s",
        (task_id, user_id)
    )
    task = cursor.fetchone()

    if not task:
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "Task not found"}), 404

    if task["status"] == "completed":
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "Task is already completed"}), 400

    # Mark completed and record the timestamp
    cursor.execute(
        "UPDATE tasks SET status = 'completed', completed_date = NOW() WHERE id = %s AND user_id = %s",
        (task_id, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "success", "message": "Task marked as completed"}), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """
    Permanently delete a task.
    Only the task's owner can delete it.
    """
    user_id = get_user_id()
    if not user_id:
        return jsonify({"status": "error", "message": "Please log in"}), 401

    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Verify ownership before deleting
    cursor.execute(
        "SELECT id FROM tasks WHERE id = %s AND user_id = %s",
        (task_id, user_id)
    )
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "Task not found"}), 404

    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "success", "message": "Task deleted"}), 200
