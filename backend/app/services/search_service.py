from ..database import get_db_connection

def save_search_query(query: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO search_history (query)
        VALUES (%s)
    """, (query,))
    conn.commit()
    cur.close()
    conn.close()


def get_recent_searches(limit: int = 5):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT ON (query) query
        FROM search_history
        ORDER BY query, id DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in rows]