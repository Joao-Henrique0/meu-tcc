from flask import request, jsonify
import os
import requests

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

def get_authenticated_user_id():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        return jsonify({"error": "Token ausente"}), 401

    user_info = verify_token_with_supabase(token)
    if not user_info:
        return jsonify({"error": "Token inválido"}), 401

    return user_info.get("id")  # ou "sub" se o ID estiver em outra chave


def verify_token_with_supabase(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": SUPABASE_API_KEY,
    }
    try:
        res = requests.get(f"{SUPABASE_URL}/auth/v1/user", headers=headers)
        if res.status_code == 200:
            return res.json()
        return None
    except Exception as e:
        print("Erro ao verificar token Supabase:", str(e))
        return None
