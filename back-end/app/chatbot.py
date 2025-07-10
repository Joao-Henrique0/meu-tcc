import re
from datetime import datetime, time, timedelta, date
from .nlp.intent_predictor import predict_intent
import spacy
from dateutil import parser as date_parser

nlp = spacy.load("pt_core_news_sm")
WEEKDAYS = ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'domingo']

def handle_message(message, user_id):
    intent, confidence = predict_intent(message)
    print(f"Intent: {intent}, Confidence: {confidence}")
    print(f"Message: {message}")
    
    if confidence < 0.6:
        return {"intent": "desconhecido", "data": None, "error": "Desculpe, não entendi muito bem. Poderia reformular?"}

    if intent == "adicionar_tarefa":
        parsed_task = parse_task_from_natural_input(message)
        return {
            "intent": "adicionar_tarefa",
            "data": parsed_task,
            "error": None if parsed_task else "Não foi possível interpretar a tarefa."
        }

    if intent == "listar_tarefas":
        return {
            "intent": "listar_tarefas",
            "data": None
        }

    if intent == "atualizar_tarefa":
        return parse_update_task(message)

    if intent == "deletar_tarefa":
        return parse_delete_task(message)

    if intent == "saudacao":
        return {
            "intent": "saudacao",
            "data": {"text": "Olá! Em que posso ajudar?"}
        }

    if intent == "despedida":
        return {
            "intent": "despedida",
            "data": {"text": "Até mais! Bom trabalho."}
        }

    return {
        "intent": "desconhecido",
        "data": None,
        "error": "Desculpe, não entendi."
    }

def parse_task_from_natural_input(message):
    try:
        now = datetime.now()
        doc = nlp(message)

        temp_date = None
        temp_hour = None
        temp_minute = None
        description = message.strip()

        if re.search(r'\bamanhã\b', message, re.IGNORECASE):
            temp_date = (now + timedelta(days=1)).date()
        elif re.search(r'\bhoje\b', message, re.IGNORECASE):
            temp_date = now.date()

        time_match = re.search(r'(\d{1,2})[:h](\d{0,2})', message)
        if time_match:
            temp_hour = int(time_match.group(1))
            temp_minute = int(time_match.group(2)) if time_match.group(2) else 0

        temp_date = temp_date or now.date()
        temp_hour = temp_hour if temp_hour is not None else 9
        temp_minute = temp_minute if temp_minute is not None else 0
        task_time = datetime.combine(temp_date, time(temp_hour, temp_minute))

        # Limpeza de texto
        description = re.sub(
            r'\b(amanhã|hoje|às?\s*\d{1,2}h\d{0,2}|\bàs?\s*\d{1,2}[:h]\d{0,2}|\bas\b)\b',
            '', description, flags=re.IGNORECASE
        )
        description = re.sub(r'^(vou|preciso|tenho que|devo|quero|favor|lembrar de|lembra de|tem que)\s+', '', description, flags=re.IGNORECASE)
        description = re.sub(r'^(no|na|nos|nas|para|ao|aos|às|o|a)\s+', '', description, flags=re.IGNORECASE)

        locais_chave = ["mercado", "padaria", "farmácia", "praia"]
        title = ""

        for local in locais_chave:
            if re.search(rf'\b{local}\b', description, re.IGNORECASE):
                title = local.capitalize()
                description = re.sub(rf'\b{local}\b', '', description, flags=re.IGNORECASE).strip()
                break

        if not title:
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"] and token.text.lower() not in locais_chave:
                    title = token.text.capitalize()
                    break

        if not title:
            title = message.split()[0].capitalize()

        description = re.sub(r'^(para|no|na|nos|nas|ao|aos|às|de|do|da|o|a)\s+', '', description, flags=re.IGNORECASE)
        description = re.sub(r'\s+', ' ', description).strip()

        if description.lower() == title.lower() or len(description.split()) <= 1:
            description = ""

        return {
            "title": title,
            "description": description,
            "time": task_time.isoformat()
        }
    except Exception as e:
        print("Erro ao interpretar tarefa:", e)
        return None

def parse_update_task(message):
    match = re.search(
        r"(remarca|muda|altera|atualiza|editar|modifica|remarcar|mudar|alterar)\s+(?:tarefa\s+)?(?P<title>.+?)\s+(?:para|pra|to)\s+(?P<new_value>.+)",
        message, re.IGNORECASE
    )
    if not match:
        return {
            "intent": "atualizar_tarefa",
            "data": None,
            "error": "Informe no formato: 'Atualizar [tarefa] para [novo horário]'"
        }

    title = match.group("title").strip()
    new_value = match.group("new_value").strip()

    try:
        old_time = datetime.now()
        new_time = parse_new_datetime(new_value, old_time)
        return {
            "intent": "atualizar_tarefa",
            "data": {
                "title": title,
                "new_time": new_time.isoformat()
            }
        }
    except Exception as e:
        return {
            "intent": "atualizar_tarefa",
            "data": None,
            "error": f"Erro ao interpretar nova data: {str(e)}"
        }

def parse_delete_task(message):
    match = re.search(r"(cancelar|excluir|deletar|remover)(?:\s+tarefa)?\s+(.*)", message, re.IGNORECASE)
    if not match:
        return {
            "intent": "deletar_tarefa",
            "data": None,
            "error": "Informe qual tarefa deseja remover. Ex: 'Cancelar dentista'"
        }
    title = match.group(2).strip()
    if title.lower().startswith("tarefa "):
        title = title[7:].strip()
    return {
        "intent": "deletar_tarefa",
        "data": {"title": title}
    }

def parse_new_datetime(new_value: str, reference_time: datetime) -> datetime:
    doc = nlp(new_value.lower())
    base_date = reference_time.date()
    hour, minute = reference_time.hour, reference_time.minute

    if "amanhã" in new_value.lower():
        base_date = datetime.now().date() + timedelta(days=1)
    elif "hoje" in new_value.lower():
        base_date = datetime.now().date()
    elif any(day in new_value.lower() for day in WEEKDAYS):
        base_date = parse_weekday(new_value, reference_time)

    time_match = re.search(r"(\d{1,2})[:h](\d{2})", new_value)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))

    try:
        if base_date == reference_time.date() and not time_match:
            return date_parser.parse(new_value, dayfirst=True)
    except:
        pass

    return datetime.combine(base_date, time(hour, minute))

def parse_weekday(text: str, reference_time: datetime) -> date:
    WEEKDAY_MAP = {
        'segunda': 0, 'terça': 1, 'quarta': 2,
        'quinta': 3, 'sexta': 4, 'sábado': 5, 'domingo': 6
    }
    today = reference_time.date()
    today_weekday = today.weekday()

    for day_name, day_idx in WEEKDAY_MAP.items():
        if day_name in text.lower():
            days_ahead = (day_idx - today_weekday) % 7
            if "próxim" in text.lower() and days_ahead == 0:
                days_ahead = 7
            return today + timedelta(days=days_ahead)

    return today

    

def update_task_completion(message, user_id):
    try:
        # Exemplo de mensagem: "Marcar tarefa comprar pão como completa"
        match = re.search(r"(marcar|atualizar|definir)\s+tarefa\s+(.*?)\s+como\s+(completa|incompleta)", message, re.IGNORECASE)
        if not match:
            return "Informe no formato: 'Marcar tarefa [título] como completa/incompleta'"

        title = match.group(2).strip()
        status_str = match.group(3).strip().lower()
        complete = True if status_str == "completa" else False

        task = get_task_by_title(user_id, title)
        if not task:
            return f"Tarefa '{title}' não encontrada."

        updated = update_task_completion_status(task["id"], user_id, complete)
        if not updated:
            return f"Erro ao atualizar o status da tarefa '{title}'."

        return f"Tarefa '{title}' atualizada para {'completa' if complete else 'incompleta'}."
    except Exception as e:
        return f"Erro ao atualizar o status da tarefa: {str(e)}"