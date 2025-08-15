from .detectors import DETECTORS
from .anomaly_service import log_anomaly
from ..database import get_db_connection
from .alert_service import save_alert, alert_exists

def run_all_detectors():
    """
    Jalankan semua detektor untuk semua wallet unik dan simpan hasil anomaly-nya ke tabel anomalies.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT sender FROM transactions
        UNION
        SELECT DISTINCT receiver FROM transactions
    """)
    wallets = [row[0] for row in cur.fetchall()]
    cur.close()

    total_inserted = 0

    for wallet in wallets:
        for name, detector_fn in DETECTORS.items():
            try:
                results = detector_fn(wallet, conn)
                for result in results:
                    metadata = result['data']
                    tx_hash = metadata.get('tx_hash')  # bisa None kalau anomaly wallet-based
                    reason  = result.get('reason') or f"{name} mendeteksi aktivitas mencurigakan"

                    log_anomaly(
                        wallet_address=wallet,
                        tx_hash=tx_hash,
                        detector=name,
                        reason=reason,
                        metadata=metadata
                    )
                    total_inserted += 1
            except Exception as e:
                print(f"Error processing {name} for {wallet}: {e}")

    conn.close()
    print(f"Total anomalies inserted: {total_inserted}")