from app.services.detectors import run_all_detectors
from app.database import get_db_connection

def get_all_wallets():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT sender FROM transactions
        UNION
        SELECT DISTINCT receiver FROM transactions
    """)
    wallets = [row[0] for row in cur.fetchall()]
    cur.close(); conn.close()
    return wallets

def run():
    wallets = get_all_wallets()
    print(f"Running heuristic detectors for {len(wallets)} wallets...")
    for i, wallet in enumerate(wallets, 1):
        print(f"[{i}/{len(wallets)}] Wallet: {wallet}")
        run_all_detectors(wallet)

if __name__ == "__main__":
    run()
