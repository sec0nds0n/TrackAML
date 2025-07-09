from flask_restx import Namespace, Resource, fields
from flask import request, current_app
import jwt
import datetime

from ..database import get_db_connection

api = Namespace('auth', description='Operasi autentikasi (login)')

# Model untuk request login
login_model = api.model('Login', {
    'username': fields.String(required=True, description='Nama pengguna'),
    'password': fields.String(required=True, description='Password')
})

# Model untuk objek user di response
auth_user = api.model('AuthUser', {
    'id': fields.Integer(description='ID pengguna'),
    'username': fields.String(description='Nama pengguna'),
    'role': fields.String(description='Peran pengguna'),
    'permissions': fields.List(fields.String, description='Daftar izin')
})

# Model untuk keseluruhan response login
login_response = api.model('LoginResponse', {
    'success': fields.Boolean(description='Status keberhasilan'),
    'token': fields.String(description='JWT untuk otentikasi'),
    'user': fields.Nested(auth_user)
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    @api.marshal_with(login_response)
    def post(self):
        """Endpoint untuk login dan mendapatkan JWT"""
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            api.abort(400, 'Username dan password harus diisi')

        # Ambil user dari DB
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, username, role
            FROM users
            WHERE username = %s
              AND password = crypt(%s, password)
            """,
            (username, password)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            api.abort(401, 'Invalid credentials')

        user_id, user_name, user_role = user

        # Generate JWT
        secret = current_app.config.get('SECRET_KEY', 'changeme')
        token = jwt.encode({
            'sub': user_id,
            'username': user_name,
            'role': user_role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, secret, algorithm='HS256')

        # Mapping permissions per role
        role_permissions = {
            'admin':      ['read', 'write', 'delete'],
            'public':     ['read'],
            'L1':         ['read', 'write'],
            'L2':         ['read', 'write'],
            'Exchanger':  ['read', 'write'],
        }

        return {
            'success': True,
            'token': token,
            'user': {
                'id': user_id,
                'username': user_name,
                'role': user_role,
                'permissions': role_permissions.get(user_role, [])
            }
        }