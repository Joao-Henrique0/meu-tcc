import pytest
from app.chatbot import handle_message

@pytest.fixture
def user_id():
    # Use um user_id válido do seu banco de dados de testes
    return "689555fc-ff77-4202-95f3-858a524d2029"

@pytest.mark.parametrize("frase", [
    "vou para a praia amanhã às 4h",
    "vou no mercado comprar pão, cebola e coentro amanhã às 9h",
    "preciso passar na padaria para comprar leite e pão amanhã às 18h",
    "indo na farmácia comprar um remédio amanhã às 13h",
    "comprar arroz e feijão no mercado amanhã às 10h",
    "comprar carne, frango e peixe no mercado amanhã às 11h",
    "comprar remédios na farmácia amanhã às 16h",
    "ir no supermercado comprar frutas amanhã às 17h",
    "vou cortar o cabelo amanhã às 15h",
    "vou no mercadinho comprar queijo amanhã às 8h",
    "passar na feira amanhã às 7h para comprar legumes",
    "vou na farmácia amanhã às 14h",
    "vou no mercado amanhã às 8h",
    "comprar bolacha na padaria amanhã às 10h",
    "ir no açougue comprar linguiça amanhã às 12h"
])

def test_adicionar_tarefa(frase):
    user_id = "689555fc-ff77-4202-95f3-858a524d2029"
    resposta = handle_message(frase, user_id)
    assert "Tarefa criada com sucesso" in resposta

def test_listar_tarefas(user_id):
    resposta = handle_message("quero ver minhas tarefas", user_id)
    assert "cabelo" in resposta or "Você não possui tarefas" in resposta

def test_atualizar_tarefa(user_id):
    resposta = handle_message("remarcar cortar o cabelo pra sexta", user_id)
    assert "remarcada para" in resposta or "não encontrada" in resposta

def test_deletar_tarefa(user_id):
    resposta = handle_message("cancelar cortar o cabelo", user_id)
    assert "foi deletada com sucesso" in resposta or "não encontrada" in resposta

def test_saudacao(user_id):
    resposta = handle_message("oi", user_id)
    assert "Olá" in resposta or "posso ajudar" in resposta

def test_despedida(user_id):
    resposta = handle_message("tchau", user_id)
    assert "Até mais" in resposta or "bom trabalho" in resposta
