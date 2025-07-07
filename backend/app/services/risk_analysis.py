from decimal import Decimal
from ..database import get_db_connection
from .kyc_service import get_wallet_summary

THRESHOLD_TX_COUNT = 50
THRESHOLD_UNIQUE_WALLETS = 20
THRESHOLD_LARGE_TX = 1000  # Dalam ETH
THRESHOLD_OUTBOUND_RATIO = Decimal("0.9")

def calculate_wallet_risk(wallet_address):
    """Menghitung profil risiko dari wallet berdasarkan transaksi yang tersimpan di database."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Ambil data transaksi wallet
    cur.execute("""
        SELECT COUNT(*) FROM transactions WHERE sender = %s
    """, (wallet_address,))
    outbound_tx = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(DISTINCT receiver) FROM transactions WHERE sender = %s
    """, (wallet_address,))
    unique_receivers = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM transactions WHERE receiver = %s
    """, (wallet_address,))
    inbound_tx = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(DISTINCT sender) FROM transactions WHERE receiver = %s
    """, (wallet_address,))
    unique_senders = cur.fetchone()[0]

    cur.execute("""
        SELECT COALESCE(SUM(value), 0) FROM transactions WHERE sender = %s
    """, (wallet_address,))
    outbound_value = float(cur.fetchone()[0])

    cur.execute("""
        SELECT COALESCE(SUM(value), 0) FROM transactions WHERE receiver = %s
    """, (wallet_address,))
    inbound_value = float(cur.fetchone()[0])

    total_value = inbound_value + outbound_value

    # Heuristic risk scoring
    risk_score = 0

    if outbound_tx > 50 or unique_receivers > 20:
        risk_score += 2  # Banyak transaksi keluar ke banyak alamat

    if inbound_tx > 50 or unique_senders > 20:
        risk_score += 2  # Banyak transaksi masuk dari banyak alamat

    if total_value > 100:  # Threshold nilai transaksi (misalnya 100 ETH)
        risk_score += 1

    if outbound_value > (total_value * 0.8):  # Jika lebih dari 80% ETH dikirim keluar
        risk_score += 1

    # Evaluasi skor risiko
    if risk_score >= 4:
        risk_profile = "High Risk"
    elif risk_score >= 2:
        risk_profile = "Medium Risk"
    else:
        risk_profile = "Low Risk"

    cur.close()
    conn.close()

    return risk_profile, risk_score

def fetch_transactions_from_db(wallet_address):
    """Mengambil wallet dari wallet_history yang belum memiliki profil risiko."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT sender, receiver, value, timestamp 
        FROM transactions 
        WHERE sender = %s OR receiver = %s
    """, (wallet_address, wallet_address))
    
    wallets = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return wallets

def get_high_risk_address_count():
    """
    Menghitung jumlah alamat di tabel wallet_risk
    dengan risk_profile = 'High Risk'.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) 
        FROM wallet_risk 
        WHERE risk_profile = 'High Risk';
    """)
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"high_risk_addresses": int(count)}

def get_risk_distribution():
    """
    Menghitung jumlah dan persentase alamat untuk masing-masing risk_profile
    di tabel wallet_risk (High, Medium, Low).
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT risk_profile, COUNT(*) AS count
        FROM wallet_risk
        WHERE risk_profile IN ('High Risk', 'Medium Risk', 'Low Risk')
        GROUP BY risk_profile;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    total = sum(c for _, c in rows) or 1

    # Urutan High → Medium → Low
    order = ["High Risk", "Medium Risk", "Low Risk"]
    dist = []
    for profile in order:
        cnt = next((c for p, c in rows if p == profile), 0)
        pct = round(cnt / total * 100, 2)
        dist.append({
            "risk_profile": profile,
            "count": cnt,
            "percentage": pct
        })

    return dist

def get_wallet_risk_cases(limit: int = 10):
    """
    Mengambil wallet terakhir yang di-risk_profiling
    dan membungkusnya sebagai AML Case, lengkap dengan saldo ETH.
    """
    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT address, risk_profile, last_updated
        FROM wallet_risk
        ORDER BY last_updated DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    cases = []
    for address, risk_profile, last_updated in rows:
        # Panggil summary yang sudah ada
        summary = get_wallet_summary(address)
        balance = summary.get("balance", 0)

        cases.append({
            "case_id":     f"AML-WR-{address}",
            "wallet":      address,
            "entity_type":"Wallet",
            "crypto":      "ETH",
            "amount":      f"{balance:.4f} ETH",
            "risk":        risk_profile,
            "status":      "Under Review",
            "date":        last_updated.date().isoformat()
        })
    return cases