from ..database import get_db_connection
from psycopg2.extras import Json, RealDictCursor

def create_notification(user_id: int, ntype: str, message: str, meta: dict | None = None):
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            INSERT INTO notifications (user_id, type, message, meta)
            VALUES (%s, %s, %s, %s::jsonb)
            RETURNING id, created_at
        """, (user_id, ntype, message, Json(meta or {})))
        row = cur.fetchone()
        return {"id": row["id"], "created_at": row["created_at"]}

def list_notifications(user_id: int, unread_only: bool = False, limit: int = 20):
    cond = "AND is_read = FALSE" if unread_only else ""
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT id, type, message, meta, is_read, created_at
            FROM notifications
            WHERE user_id = %s {cond}
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        return cur.fetchall()

def mark_all_read(user_id: int):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s AND is_read = FALSE", (user_id,))
        conn.commit()