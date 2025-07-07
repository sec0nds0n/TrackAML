from .detectors import DETECTORS
from ..database import get_db_connection
from .alert_service import save_alert, alert_exists

def run_all_detectors():
    conn = get_db_connection()

    # 1) Ambil semua wallet
    cur = conn.cursor()
    cur.execute("SELECT address FROM wallet_history")
    wallets = [r[0] for r in cur.fetchall()]
    cur.close()

    # 2) Untuk setiap wallet dan detektor
    for wallet in wallets:
        for name, detector_fn in DETECTORS.items():
            results = detector_fn(wallet, conn)
            for res in results:
                ts = res['data']['timestamp']
                # 3) Simpan hanya jika belum ada
                if not alert_exists(conn, wallet, name, ts):
                    save_alert(wallet, name, res['data'])

    conn.close()