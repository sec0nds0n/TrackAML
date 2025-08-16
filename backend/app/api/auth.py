from flask_restx import Namespace, Resource, fields
from flask import request, current_app, jsonify, make_response, g  # ⬅️ tambahkan g
from psycopg2.extras import RealDictCursor
import jwt, datetime, secrets

from ..database import get_db_connection
from ..utils import jwt_required

api = Namespace('auth', description='Operasi autentikasi (login)')

login_model = api.model('Login', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})

user_model = api.model('User', {
    'id': fields.Integer,
    'username': fields.String,
    'role': fields.String,
    'permissions': fields.List(fields.String)
})

def _role_permissions(role):
    return {
        'admin':      ['read', 'write', 'assign', 'manage_users'],
        'analyst_L1': ['read', 'write'],
        'analyst_L2': ['read', 'write', 'assign'],
        'Exchanger':  ['read', 'write']
    }.get(role, [])

def _issue_tokens(user):
    now = datetime.datetime.utcnow()
    exp = now + datetime.timedelta(hours=8)
    perms = _role_permissions(user['role'])
    payload = {
        'sub': str(user['id']),  # <— penting: string
        'username': user['username'],
        'role': user['role'],
        'permissions': perms,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8),
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    csrf = secrets.token_urlsafe(24)
    return token, csrf, exp

def _set_auth_cookies(resp, token, csrf, exp):
    secure = bool(current_app.config.get('COOKIE_SECURE', True))
    samesite = current_app.config.get('COOKIE_SAMESITE', 'None')
    resp.set_cookie('access_token', token, httponly=True, secure=secure, samesite=samesite, expires=exp, path='/')
    resp.set_cookie('csrf_token', csrf, httponly=False, secure=secure, samesite=samesite, expires=exp, path='/')
    return resp

@api.route('/login')
class Login(Resource):
    @api.expect(login_model, validate=True)
    def post(self):
        data = request.get_json() or {}
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()
        if not username or not password:
            return {'success': False, 'message': 'Username/password required'}, 400

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, username, role
            FROM users
            WHERE username = %s AND password = crypt(%s, password)
            LIMIT 1
        """, (username, password))
        user = cur.fetchone()
        cur.close(); conn.close()

        if not user:
            return {'success': False, 'message': 'Invalid credentials'}, 401

        token, csrf, exp = _issue_tokens(user)
        body = {
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'permissions': _role_permissions(user['role'])
            }
        }
        resp = make_response(jsonify(body), 200)
        _set_auth_cookies(resp, token, csrf, exp)
        return resp

@api.route('/me')
class Me(Resource):
    @jwt_required
    def get(self):
        return {
            'success': True,
            'user': {
                'id': g.user_id,
                'username': g.username,
                'role': g.role,
                'permissions': getattr(g, 'permissions', []) or [],
            }
        }, 200

@api.route('/logout')
class Logout(Resource):
    def post(self):
        resp = make_response(jsonify({'success': True}), 200)
        # pakai flag yang sama dgn saat set cookie
        secure = bool(current_app.config.get('COOKIE_SECURE', True))
        samesite = current_app.config.get('COOKIE_SAMESITE', 'None')
        resp.set_cookie('access_token', '', expires=0, httponly=True,  secure=secure, samesite=samesite)
        resp.set_cookie('csrf_token',   '', expires=0, httponly=False, secure=secure, samesite=samesite)
        return resp
    
@api.route('/csrf')
class Csrf(Resource):
    def get(self):
        # token sudah diset saat login sebagai cookie 'csrf_token'
        # endpoint ini hanya meng-echo saja bila ada
        from flask import request, jsonify
        token = request.cookies.get('csrf_token')
        return jsonify({'csrf_token': token})