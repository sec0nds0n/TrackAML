from app.users.routes import users_bp
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, template_folder='templates/auth')