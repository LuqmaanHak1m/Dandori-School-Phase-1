import logging
from flask import Flask
from dotenv import load_dotenv
from .config import Config

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.logger.setLevel(getattr(logging, Config.LOG_LEVEL, logging.INFO))

    from .routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app