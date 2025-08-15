from ..database import get_db_connection
from psycopg2.extras import RealDictCursor

def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, username, role FROM users ORDER BY id")
    users = cur.fetchall()
    cur.close(); conn.close()
    return users
