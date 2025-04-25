from flask import Flask
from flask_cors import CORS
from .routes import routes
from .tasks import tasks_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(routes)
    app.register_blueprint(tasks_bp)
    return app
