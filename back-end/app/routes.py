from flask import Blueprint, request, jsonify
from .chatbot import handle_message # ajuste o nome se o caminho for diferente

routes = Blueprint("routes", __name__)

@routes.route("/chatbot", methods=["POST"])
def chatbot_response():
    data = request.get_json()
    user_input = data.get("message", "")
    
    if not user_input:
        return jsonify({"error": "Mensagem não fornecida."}), 400

    response = handle_message(user_input)
    return jsonify({"response": response}), 200
