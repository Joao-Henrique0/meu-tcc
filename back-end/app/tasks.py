from flask import Blueprint, request, jsonify
from .db import get_connection
import uuid
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/tasks", methods=["GET"])
def list_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks ORDER BY time ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    tasks = [{
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "time": row[3].isoformat(),
        "complete": row[4]
    } for row in rows]
    return jsonify(tasks), 200

@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    task_id = str(uuid.uuid4())
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tasks (id, title, description, time, complete)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        task_id,
        data["title"],
        data.get("description", ""),
        data.get("time"),
        False
    ))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": task_id}), 201

@tasks_bp.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return jsonify({"error": "Tarefa não encontrada"}), 404

    task = {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "time": row[3].isoformat(),
        "complete": row[4]
    }
    return jsonify(task), 200

@tasks_bp.route("/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE tasks
        SET title = %s,
            description = %s,
            time = %s,
            complete = %s
        WHERE id = %s
    """, (
        data.get("title"),
        data.get("description"),
        data.get("time"),
        data.get("complete"),
        task_id
    ))

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Tarefa atualizada com sucesso"}), 200

@tasks_bp.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Tarefa removida com sucesso"}), 200
