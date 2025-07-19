import re
from datetime import datetime, time, timedelta, date
from .nlp.intent_predictor import predict_intent
import spacy
from dateutil import parser as date_parser
import dateparser

nlp = spacy.load("pt_core_news_sm")

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
        return {
            "intent": "atualizar_tarefa",
            "data": parse_update_task(message),
            "error": None if parse_update_task(message) else "Não foi possível interpretar a atualização da tarefa."
        }

    if intent == "deletar_tarefa":
        return {
            "intent": "deletar_tarefa",
            "data": parse_delete_task(message),
            "error": None if parse_delete_task(message) else "Não foi possível interpretar a exclusão da tarefa."
        }

    if intent == "saudacao":
        return {
            "intent": "saudacao",
            "data": {"text": "Olá! Em que posso ajudar?"}
        }

    if intent == "despedida":
        return {
            "intent": "despedida",
            "data": {"text": "Até mais!."}
        }

    return {
        "intent": "desconhecido",
        "data": None,
        "error": "Desculpe, não entendi."
    }

PERIODS_OF_THE_DAY = {
    "manhã": time(9, 0),
    "tarde": time(14, 0),
    "noite": time(19, 0),
    "almoço": time(12, 0),
    "jantar": time(20, 0),
}

RELATIVE_EXPRESSIONS = {
    "depois de amanhã": timedelta(days=2),
    "amanhã": timedelta(days=1),
    "hoje": timedelta(days=0),
    "ontem": timedelta(days=-1),
    "semana que vem": timedelta(days=7),
    "próxima semana": timedelta(days=7),
}

KEY_LOCATIONS = [
    "mercado", "padaria", "farmácia", "praia", "academia",
    "escola", "trabalho", "shopping", "cinema", "parque"
]

def adjust_period_of_day(message: str, base_datetime: datetime) -> datetime:
    for periodo, horario in PERIODS_OF_THE_DAY.items():
        if re.search(rf"\b{periodo}\b", message, re.IGNORECASE):
            return base_datetime.replace(hour=horario.hour, minute=horario.minute)
    return base_datetime

def apply_relative_expression(message: str) -> datetime | None:
    now = datetime.now()
    for expressao, delta in RELATIVE_EXPRESSIONS.items():
        if expressao in message.lower():
            return now + delta
    return None

def clear_text(texto: str) -> str:
    texto = texto.strip()
    texto = re.sub(
        r'\b(amanhã|hoje|depois de amanhã|ontem|semana que vem|próxima semana|à noite|de manhã|à tarde|de tarde|ao meio-dia|às?\s*\d{1,2}[:h]?\d{0,2}?)\b',
        '', texto, flags=re.IGNORECASE
    )
    texto = re.sub(r'\b(vou|preciso|tenho que|devo|quero|favor|lembrar de|lembra de|anotar|tem que|marcar|ir ao|ir à|passar no|comprar no)\b',
                   '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\b(no|na|nos|nas|ao|aos|às|o|a|de|do|da)\b', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def extract_datetime(message: str) -> datetime:
    dt_base = apply_relative_expression(message)
    if not dt_base:
        dt_base = dateparser.parse(message, languages=['pt']) or datetime.now()

    # Ajusta o período do dia se houver palavras-chave
    dt_ajustado = adjust_period_of_day(message, dt_base)

    # Extração manual de hora/minuto se houver "às", "as", ":" ou "h"
    hora_match = re.search(r"(?:às|as)?\s*(\d{1,2})[:h]?(\d{0,2})", message)
    if hora_match:
        hour = int(hora_match.group(1))
        minute = int(hora_match.group(2)) if hora_match.group(2) else 0
        dt_ajustado = dt_ajustado.replace(hour=hour, minute=minute)
    elif dt_ajustado.hour == 0 and "às" not in message and ":" not in message and "h" not in message:
        dt_ajustado = dt_ajustado.replace(hour=9, minute=0)  # default: 9h

    return dt_ajustado


def extract_location(doc, texto):
    # Primeiro tenta por entidade do spaCy
    for ent in doc.ents:
        if ent.label_ == "LOC":
            return ent.text.capitalize()

    # Fallback com regex por palavras-chave conhecidas
    for local in KEY_LOCATIONS:
        if re.search(rf'\b{local}\b', texto, re.IGNORECASE):
            return local.capitalize()

    return None

def extract_title(doc, texto):
    local = extract_location(doc, texto)
    if local:
        return local

    for token in doc:
        if token.dep_ in ["obj", "ROOT"] and token.pos_ in ["NOUN", "PROPN"]:
            return token.text.capitalize()

    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"]:
            return token.text.capitalize()

    return texto.split()[0].capitalize()

def parse_task_from_natural_input(message):
    try:
        task_time = extract_datetime(message)
        description = clear_text(message)
        doc_limpo = nlp(description)
        title = extract_title(doc_limpo, description)

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
    # Captura título e novo valor com mais flexibilidade
    match = re.search(
        r"(remarca|muda|altera|atualiza|editar|modifica|remarcar|mudar|alterar)\s+(?:a\s+)?(?:tarefa\s+)?(?P<title>.+?)\s+(?:para|pra|to)\s+(?P<new_value>.+)",
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
        # Usa a mesma função de extração de data/hora da tarefa principal
        new_time = extract_datetime(new_value)

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
    match = re.search(
        r"\b(cancelar|excluir|deletar|remover)\b\s*(?:a\s+)?(?:tarefa\s+)?(?P<title>.+)",
        message, re.IGNORECASE
    )

    if not match:
        return {
            "intent": "deletar_tarefa",
            "data": None,
            "error": "Informe qual tarefa deseja remover. Ex: 'Cancelar dentista'"
        }

    title = match.group("title").strip()

    # Evita inputs como apenas "tarefa" ou "a"
    if not title or title.lower() in ["tarefa", "a tarefa", "a"]:
        return {
            "intent": "deletar_tarefa",
            "data": None,
            "error": "O nome da tarefa está incompleto. Ex: 'Excluir mercado'"
        }

    return {
        "intent": "deletar_tarefa",
        "data": {"title": title}
    }

    

def update_task_completion(message, user_id):
    try:
        # Exemplo de mensagem: "Atualizar tarefa comprar pão para completa"
        match = re.search(
            r"(atualizar)\s+tarefa\s+(.*?)\s+para\s+(completa|incompleta)",
            message, re.IGNORECASE
        )
        if not match:
            return {
                "intent": "atualizar_tarefa",
                "data": None,
                "error": "Informe no formato: 'Atualizar tarefa [título] para completa/incompleta'"
            }

        title = match.group(2).strip()
        status_str = match.group(3).strip().lower()
        complete = True if status_str == "completa" else False

        # Aqui você pode implementar a lógica de atualização diretamente no frontend ou em memória.
        # Exemplo de retorno esperado:
        return {
            "intent": "atualizar_tarefa",
            "data": {
                "title": title,
                "complete": complete
            },
            "error": None
        }
    except Exception as e:
        return {
            "intent": "atualizar_tarefa",
            "data": None,
            "error": f"Erro ao atualizar o status da tarefa: {str(e)}"
        }