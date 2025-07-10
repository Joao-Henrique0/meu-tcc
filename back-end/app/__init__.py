from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .routes import routes
import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configuração do JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")  # Substitua por uma chave segura
    app.config["JWT_DECODE_LEEWAY"] = 10 
    jwt = JWTManager(app)

    app.register_blueprint(routes)
    return app