from functools import wraps
from flask import session, abort

def roles_required(*allowed_roles):
    """
    Decorator untuk membatasi akses view berdasarkan role.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if session.get('role') not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator