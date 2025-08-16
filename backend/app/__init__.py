from flask import Flask, redirect, url_for
from dotenv import load_dotenv
from flask_cors import CORS
import os

from .config import Config
from .extensions import flask_session_ext, neo4j_driver

from .auth.routes import auth_bp
from .aml.routes import aml_bp
from app.api.routes import api_bp
from app.users.routes import users_bp

def create_app():
    load_dotenv()

    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)

    # SECRET_KEY konsisten
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', app.config.get('SECRET_KEY') or 'dev-secret-trackaml')
    app.secret_key = app.config['SECRET_KEY']
    os.makedirs(app.config['UPLOAD_DIR'], exist_ok=True)

    # CORS + credentials
    CORS(app,
         resources={r"/api/*": {"origins": ["http://127.0.0.1:5173", "http://localhost:5173"]}},
         supports_credentials=True,
         allow_headers=["Content-Type", "X-Csrf-Token"],
         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])

    @app.route('/')
    def home():
        return redirect(url_for('aml.wallet'))

    flask_session_ext.init_app(app)
    neo4j_driver.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(aml_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(users_bp)

    return app