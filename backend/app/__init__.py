import os
from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from .config import Config
from .extensions import flask_session_ext, neo4j_driver
from .auth.routes import auth_bp
from .aml.routes import aml_bp
from app.api.routes import api_bp
from app.users.routes import users_bp
from apscheduler.schedulers.background import BackgroundScheduler
from .services.scheduler import run_all_detectors

def create_app():
    load_dotenv()
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object('app.config.Config')
    CORS(app)
    # Initialize extensions
    from flask import session, redirect, url_for
    @app.route('/')
    def home():
        if 'username' in session:
            # redirect ke wallet di blueprint AML
            return redirect(url_for('aml.wallet'))
        # redirect ke login di blueprint Auth
        return redirect(url_for('auth.login'))

    # Initialize extensions
    flask_session_ext.init_app(app)
    neo4j_driver.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(aml_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(users_bp)
    return app

# scheduler = BackgroundScheduler(timezone='Asia/Jakarta')
# scheduler.add_job(run_all_detectors, 'cron', minute=0)  # tiap jam
# scheduler.start()