from flask_restx import Namespace, Resource, fields
from flask import request
from ..database import get_db_connection
from app.utils import roles_required

# Define the Namespace for User APIs
api = Namespace(
    'users',
    description='Operasi terkait pengguna'
)

# Model for representing a User in responses
user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description='ID pengguna'),
    'username': fields.String(required=True, description='Nama pengguna'),
    'role': fields.String(
        required=True,
        description='Peran pengguna',
        enum=['public', 'admin', 'L1', 'L2', 'Exchanger']
    ),
    'created_at': fields.DateTime(description='Timestamp pembuatan')
})

# Model for user creation request
new_user_model = api.model('NewUser', {
    'username': fields.String(required=True, description='Nama pengguna'),
    'password': fields.String(required=True, description='Password'),
    'role': fields.String(
        description='Peran pengguna',
        enum=['public', 'admin', 'L1', 'L2', 'Exchanger'],
        default='public'
    )
})

# Model for user update request
edit_user_model = api.model('EditUser', {
    'username': fields.String(required=True, description='Nama pengguna baru'),
    'role': fields.String(
        required=True,
        description='Peran baru pengguna',
        enum=['public', 'admin', 'L1', 'L2', 'Exchanger']
    )
})

@api.route('')
class UserList(Resource):
    @api.doc('list_users')
    @api.marshal_list_with(user_model)
    @roles_required('admin')
    def get(self):
        """List semua pengguna"""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, role, created_at FROM users ORDER BY id")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [
            {'id': r[0], 'username': r[1], 'role': r[2], 'created_at': r[3]}
            for r in rows
        ]

    @api.doc('create_user')
    @api.expect(new_user_model)
    @api.response(201, 'User created')
    @roles_required('admin')
    def post(self):
        """Buat pengguna baru"""
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'public')
        if not username or not password or role not in ['public', 'admin', 'L1', 'L2', 'Exchanger']:
            api.abort(400, 'Invalid payload')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, role, created_at)"
            " VALUES (%s, crypt(%s, gen_salt('bf')), %s, NOW()) RETURNING id",
            (username, password, role)
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return {'id': new_id}, 201

@api.route('/<int:user_id>')
@api.param('user_id', 'ID pengguna')
class UserResource(Resource):
    @api.doc('delete_user')
    @api.response(204, 'User deleted')
    @roles_required('admin')
    def delete(self, user_id):
        """Hapus pengguna berdasarkan ID"""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        return '', 204

    @api.doc('update_user')
    @api.expect(edit_user_model)
    @roles_required('admin')
    def put(self, user_id):
        """Perbarui pengguna berdasarkan ID"""
        data = request.get_json() or {}
        username = data.get('username')
        role = data.get('role')
        if not username or role not in ['public', 'admin', 'L1', 'L2', 'Exchanger']:
            api.abort(400, 'Invalid payload')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET username = %s, role = %s WHERE id = %s",
            (username, role, user_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return {'status': 'ok'}