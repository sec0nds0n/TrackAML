import json
from ..database import get_db_connection

def save_alert(wallet, detector, payload):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO alerts(wallet_address, detector_name, payload)
        VALUES (%s, %s, %s)
    """, (wallet, detector, json.dumps(payload)))
    conn.commit()
    cur.close()
    conn.close()
    
def alert_exists(conn, wallet_address, detector_name, timestamp):
    """
    Cek apakah alert dengan wallet, nama detektor, dan timestamp yang sama
    sudah ada di tabel alerts.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT 1
        FROM alerts
        WHERE wallet_address = %s
          AND detector_name = %s
          AND (payload->>'timestamp')::float = %s
    """, (wallet_address, detector_name, timestamp))
    exists = cur.fetchone() is not None
    cur.close()
    return exists
