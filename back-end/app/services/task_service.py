import uuid
import unicodedata
from datetime import datetime

# Simula o armazenamento em memória
TASKS = []

def normalize(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def list_user_tasks(user_id):
    return [task for task in TASKS if task["user_id"] == user_id]

def create_task_for_user(user_id, title, description, time):
    task = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "description": description,
        "time": time if isinstance(time, str) else datetime.fromisoformat(time).isoformat(),
        "complete": False
    }
    TASKS.append(task)
    return task

def get_task_by_id(task_id, user_id):
    for task in TASKS:
        if task["id"] == task_id and task["user_id"] == user_id:
            return task
    return None

def get_task_by_title(user_id, title):
    search_words = set(normalize(title).split())
    for task in TASKS:
        if task["user_id"] == user_id:
            task_title_norm = normalize(task["title"])
            if all(word in task_title_norm for word in search_words):
                return task
    return None

def update_task_for_user(task_id, user_id, title, description, time, complete):
    for task in TASKS:
        if task["id"] == task_id and task["user_id"] == user_id:
            task["title"] = title
            task["description"] = description
            task["time"] = time if isinstance(time, str) else datetime.fromisoformat(time).isoformat()
            task["complete"] = complete
            return task
    return None

def delete_task_for_user(task_id, user_id):
    global TASKS
    for i, task in enumerate(TASKS):
        if task["id"] == task_id and task["user_id"] == user_id:
            deleted = TASKS.pop(i)
            return deleted
    return None

def update_task_completion_status(task_id, user_id, complete):
    for task in TASKS:
        if task["id"] == task_id and task["user_id"] == user_id:
            task["complete"] = complete
            return task
    return None