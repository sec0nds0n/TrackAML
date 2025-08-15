from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from functools import wraps
from ..database import get_db_connection
from ..utils import jwt_required, jwt_roles_required, roles_required

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/')
# @jwt_required
# @jwt_roles_required('admin')
def list_users():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT id, username, created_at FROM users ORDER BY id")
    users = cur.fetchall()
    cur.close(); conn.close()
    return render_template('users/user_list.html', users=users)

@users_bp.route('/edit/<int:user_id>', methods=['GET','POST'])
# @jwt_required
# @jwt_roles_required('admin')
def edit_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        newname = request.form['username'].strip()
        newrole = request.form['role']
        if newrole not in ['admin', 'L1', 'L2', 'Exchanger']:
            flash('Role tidak valid', 'danger')
            return redirect(url_for('users.edit_user', user_id=user_id))
        cur.execute(
            "UPDATE users SET username=%s, role=%s WHERE id=%s",
            (newname, newrole, user_id)
        )
        conn.commit()
        cur.close(); conn.close()
        flash('User berhasil di-update.', 'success')
        return redirect(url_for('users.list_users'))
    
    cur.execute("SELECT id, username, role FROM users WHERE id=%s", (user_id,))
    row = cur.fetchone()
    if not row:
        flash('User tidak ditemukan.', 'danger')
        return redirect(url_for('users.list_users'))
    user = {'id': row[0], 'username': row[1], 'role': row[2]}
    cur.close(); conn.close()
    return render_template('users/user_edit.html', user=user)

@users_bp.route('/delete/<int:user_id>')
# @jwt_required
@jwt_roles_required('admin')
def delete_user(user_id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM case_assignments WHERE user_id = %s", (user_id,))
    if cur.fetchone()[0] > 0:
        flash('Tidak bisa hapus user karena masih memiliki assignment.', 'danger')
        return redirect(url_for('users.list_users'))
    
    cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
    row = cur.fetchone()
    if not row:
        flash('User tidak ditemukan.', 'danger')
        return redirect(url_for('users.list_users'))
    conn.commit(); cur.close(); conn.close()
    flash('User dihapus.', 'warning')
    return redirect(url_for('users.list_users'))