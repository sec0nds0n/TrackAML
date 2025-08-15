from functools import wraps
from flask import g, request, jsonify, abort, current_app, session, redirect, url_for 
import jwt
import time

WRITE_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}

def _json_error(msg, code=401):
    resp = jsonify({'message': msg})
    resp.status_code = code
    return resp

def _get_bearer_token_from_header():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth.split(' ', 1)[1].strip()
    return None

def _get_token_from_cookie():
    return request.cookies.get('access_token')

def _require_csrf_if_needed():
    if request.method == 'OPTIONS':
        return
    if request.method not in WRITE_METHODS:
        return
    if request.path.endswith('/api/auth/login') or request.path.endswith('/api/auth/logout'):
        return
    if _get_token_from_cookie():
        csrf_cookie = request.cookies.get('csrf_token')
        csrf_header = request.headers.get('X-CSRF-Token')
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            abort(403, description='CSRF validation failed')
            
def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if session.get('role') not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrapper

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _get_token_from_cookie() or _get_bearer_token_from_header()
        if not token:
            return _json_error('Missing or invalid token', 401)
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256'],
                options={'require': ['exp', 'iat']},
                leeway=60,
            )
        except jwt.ExpiredSignatureError:
            return _json_error('Token expired', 401)
        except jwt.InvalidTokenError as e:
            current_app.logger.warning(f'JWT invalid: {e.__class__.__name__}: {e}')
            return _json_error('Invalid token', 401)

        g.user_id = payload.get('sub')
        g.username = payload.get('username')
        g.role = payload.get('role')
        g.permissions = payload.get('permissions', [])

        r = _require_csrf_if_needed()
        if r is not None:
            return r

        return f(*args, **kwargs)
    return decorated

def jwt_roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if getattr(g, 'role', None) not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator