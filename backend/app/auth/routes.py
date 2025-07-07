from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..database import get_db_connection
from flask import session
import psycopg2.extras

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
aml_bp = Blueprint('aml', __name__, url_prefix='/aml')

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))

@aml_bp.route('/unprocessed')
def unprocessed_wallets():
    # ambil data unprocessed…
    return render_template('aml/unprocessed_wallets.html', wallets=wallets)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT id, username, role FROM users "
            "WHERE username = %s AND password = crypt(%s, password)",
            (username, password)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            session['username'] = username
            session['role'] = user['role']
            flash("Login berhasil! Selamat datang.", "success")
            # arahkan ke halaman wallet di blueprint AML
            return redirect(url_for('aml.wallet'))
        else:
            flash("Login gagal! Periksa kembali username dan password.", "danger")
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, created_at) "
            "VALUES (%s, crypt(%s, gen_salt('bf')), NOW())",
            (username, password)
        )
        conn.commit()
        cur.close(); conn.close()
        flash('Registrasi berhasil. Silakan login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')
