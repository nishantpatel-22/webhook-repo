from flask import Flask
from app.webhook.routes import webhook

def create_app():
    app = Flask(__name__)

    # Registering the Blueprint
    # This connects the routes you wrote in app/webhook/routes.py to the main app
    app.register_blueprint(webhook)

    return app