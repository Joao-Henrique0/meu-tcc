import re
from datetime import datetime, timedelta
import uuid
from .db import get_connection
from .utils.nlp_helper import preprocess_text

def handle_message(message):
    tokens = preprocess_text(message)

    if any(t in tokens for t in ["listar", "mostrar", "ver", "tarefas", "compromissos"]):
        if match := re.search(r"(amanh\u00e3|hoje|dia \d{1,2})", message):
            return list_tasks_by_date(match.group(1).lower())
        return list_tasks()

    if any(t in tokens for t in ["atualizar", "editar", "modificar"]):
        return update_task_by_title_and_date(message)

    if any(t in tokens for t in ["deletar", "remover", "apagar"]):
        return delete_task_by_title_and_date(message)

    parsed_task = parse_task_from_natural_input(message)
    if parsed_task:
        task_id = create_task(parsed_task["title"], parsed_task["description"], parsed_task["time"])
        return f"Tarefa criada com sucesso com ID {task_id}!"

    if any(t in tokens for t in ["concluir", "finalizar", "completar"]):
        id_match = re.search(r"\b[0-9a-f\-]{36}\b", message)
        if id_match:
            task_id = id_match.group()
            mark_complete(task_id)
            return f"Tarefa {task_id} concluída!"
        return "Informe o ID da tarefa para marcá-la como concluída."

    return "Desculpe, não entendi. Você pode dizer algo como 'Tenho que ir ao dentista amanhã às 14 horas para uma obturação'."

def list_tasks_by_date(date_str):
    now = datetime.now()
    if date_str == "amanhã":
        target_day = now + timedelta(days=1)
    elif date_str == "hoje":
        target_day = now
    elif match := re.search(r"dia (\d{1,2})", date_str):
        day = int(match.group(1))
        target_day = now.replace(day=day)
    else:
        return "Data não reconhecida."

    start = target_day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = target_day.replace(hour=23, minute=59, second=59, microsecond=999999)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT title, time, complete FROM tasks WHERE time BETWEEN %s AND %s ORDER BY time ASC", (start, end))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return f"Você não possui tarefas para {date_str}."

    lines = []
    for t in rows:
        status = "✅" if t[2] else "🔘"
        lines.append(f"{status} {t[0]} às {t[1].strftime('%H:%M')}")
    return "\n".join(lines)

def parse_task_from_natural_input(message):
    try:
        title_match = re.search(r"tenho que (.+?) (amanhã|hoje|dia \d{1,2})", message, re.IGNORECASE)
        description_match = re.search(r"para (.+)$", message, re.IGNORECASE)
        time_match = re.search(r"(\d{1,2})\s*(horas|h|h\.|hs)\b", message, re.IGNORECASE)
        hour_words = {
            "uma": 1, "duas": 2, "três": 3, "quatro": 4, "cinco": 5,
            "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10,
            "onze": 11, "doze": 12
        }
        word_hour_match = re.search(r"(uma|duas|três|quatro|cinco|seis|sete|oito|nove|dez|onze|doze)\s*(da tarde|da manhã)?", message, re.IGNORECASE)

        now = datetime.now()
        if "amanhã" in message:
            task_date = now + timedelta(days=1)
        elif "hoje" in message:
            task_date = now
        elif match := re.search(r"dia (\d{1,2})", message):
            task_date = now.replace(day=int(match.group(1)))
        else:
            task_date = now

        if time_match:
            hour = int(time_match.group(1))
        elif word_hour_match:
            hour = hour_words.get(word_hour_match.group(1).lower(), 9)
            if word_hour_match.group(2) and "tarde" in word_hour_match.group(2).lower():
                if hour < 12:
                    hour += 12
        else:
            hour = 9

        task_time = task_date.replace(hour=hour, minute=0, second=0, microsecond=0)

        title = title_match.group(1).strip().capitalize() if title_match else "Compromisso"
        description = description_match.group(1).strip().capitalize() if description_match else "Sem descrição"

        return {
            "title": title,
            "description": description,
            "time": task_time.isoformat()
        }
    except Exception:
        return None

def create_task(title, description, time):
    conn = get_connection()
    cur = conn.cursor()
    task_id = str(uuid.uuid4())

    cur.execute("""
        INSERT INTO tasks (id, title, description, time, complete)
        VALUES (%s, %s, %s, %s, %s)
    """, (task_id, title, description, time, False))

    conn.commit()
    cur.close()
    conn.close()
    return task_id

def list_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT title, time, complete FROM tasks ORDER BY time ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return "Você não possui tarefas no momento."

    lines = []
    for t in rows:
        status = "✅" if t[2] else "🔘"
        lines.append(f"{status} {t[0]} às {t[1].strftime('%d/%m %H:%M')}")
    return "\n".join(lines)

def mark_complete(task_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET complete = true WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()

def update_task_by_title_and_date(message):
    try:
        # Expressão regular para capturar variações na escrita
        match = re.search(
            r"(atualizar|modificar|editar)\s+(.+?)\s+(amanhã|hoje|dia\s+\d{1,2}),?\s+para\s+(.+?)(\s+às\s+(\d{1,2}:\d{2}))?",
            message,
            re.IGNORECASE
        )
        if not match:
            return "Informe a tarefa no formato: 'Atualizar [título] [data], para [novo título] às [horário opcional]'."

        old_title = match.group(2).strip()
        date_str = match.group(3).lower()
        new_title = match.group(4).strip()
        new_time = match.group(6)  # Pode ser None se o horário não for informado

        # Determinar a data da tarefa
        now = datetime.now()
        if date_str == "amanhã":
            task_date = now + timedelta(days=1)
        elif date_str == "hoje":
            task_date = now
        elif date_match := re.search(r"dia (\d{1,2})", date_str):
            task_date = now.replace(day=int(date_match.group(1)))
        else:
            return "Data não reconhecida."

        # Determinar o horário, se fornecido
        if new_time:
            hour, minute = map(int, new_time.split(":"))
            task_time = task_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        else:
            task_time = None

        # Construir a query de atualização
        updates = ["title = %s"]
        params = [new_title]

        if task_time:
            updates.append("time = %s")
            params.append(task_time)

        params.extend([old_title, task_date.replace(hour=0, minute=0, second=0, microsecond=0), task_date.replace(hour=23, minute=59, second=59, microsecond=999999)])
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE title = %s AND time BETWEEN %s AND %s"

        # Executar a atualização no banco de dados
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, tuple(params))
        conn.commit()
        cur.close()
        conn.close()

        return f"Tarefa '{old_title}' atualizada com sucesso para '{new_title}'!"
    except Exception as e:
        return f"Erro ao atualizar a tarefa: {str(e)}"
    
def delete_task_by_title_and_date(message):
    try:
        title_match = re.search(r"título (.+?) (amanhã|hoje|dia \d{1,2})", message, re.IGNORECASE)
        if not title_match:
            return "Informe o título e a data da tarefa que deseja deletar."

        title = title_match.group(1).strip()
        date_str = title_match.group(2).lower()

        now = datetime.now()
        if date_str == "amanhã":
            task_date = now + timedelta(days=1)
        elif date_str == "hoje":
            task_date = now
        elif match := re.search(r"dia (\d{1,2})", date_str):
            task_date = now.replace(day=int(match.group(1)))
        else:
            return "Data não reconhecida."

        start = task_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = task_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE title = %s AND time BETWEEN %s AND %s", (title, start, end))
        conn.commit()
        cur.close()
        conn.close()

        return f"Tarefa '{title}' deletada com sucesso!"
    except Exception as e:
        return f"Erro ao deletar a tarefa: {str(e)}"