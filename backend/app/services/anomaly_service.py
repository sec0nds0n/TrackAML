from ..database import get_db_connection
import json
import datetime

def log_anomaly(wallet_address: str, detector: str, reason: str, metadata: dict = None, tx_hash: str = None, score: float = None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO anomalies (wallet_address, detector, reason, metadata, tx_hash, score, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        wallet_address,
        detector,
        reason,
        json.dumps(metadata or {}, default=str),
        tx_hash,
        score,
        datetime.datetime.utcnow()
    ))
    conn.commit()
    cur.close(); conn.close()