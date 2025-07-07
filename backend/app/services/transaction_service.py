from ..database import get_db_connection
from neo4j import GraphDatabase
from collections import Counter,defaultdict
from datetime import datetime
import hashlib
# Konfigurasi koneksi ke Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

neo4j_conn = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

def get_transaction_analysis(wallet_address):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT timestamp, value 
        FROM transactions 
        WHERE sender = %s OR receiver = %s
        ORDER BY timestamp ASC
    """, (wallet_address, wallet_address))

    data = cur.fetchall()
    cur.close()
    conn.close()

    timestamps = [row[0].strftime("%Y-%m-%d %H:%M:%S") for row in data]
    values = [row[1] for row in data]

    return timestamps, values

def get_transitive_risk_graph(wallet_address: str, max_hops: int = 3, limit: int = 50):
    """
    Kembalikan list of nodes (id,color), edges (from,to,label), dan legend,
    hanya berdasarkan blacklist_source → target wallet dalam max_hops.
    """
    # 1) Temukan direct blacklist nodes + hops
    cypher = f"""
        MATCH p=(t:Wallet {{address:$addr}})-[*1..{max_hops}]-(b:Wallet)
        WHERE b.is_blacklisted = true
        WITH DISTINCT b, length(p) AS hops
        RETURN b.address AS blacklist_source, hops
        LIMIT $limit
    """

    with neo4j_conn.session() as sess:
        records = sess.run(cypher, addr=wallet_address, limit=limit)

        nodes_map = {}
        edges     = []

        # Tambahkan target wallet sebagai pusat graph (biru)
        nodes_map[wallet_address] = {"id": wallet_address, "color": "#0d6efd"}

        for r in records:
            src = r["blacklist_source"]
            hops = r["hops"]

            # node blacklist (merah)
            if src not in nodes_map:
                nodes_map[src] = {"id": src, "color": "#dc3545"}

            # edge src → target
            edges.append({
                "from": src,
                "to":   wallet_address,
                "label": f"{hops} hop"
            })

    nodes = list(nodes_map.values())
    color_legend = {n["id"]: n["color"] for n in nodes}

    return nodes, edges, color_legend

def get_transactions_from_neo4j(wallet=None, sort_by="timestamp", order="desc", limit=10, offset=0):
    """Mengambil transaksi dari Neo4j dengan filter dan sorting"""
    query = """
    MATCH (s:Wallet)-[t:SEND]->(r:Wallet)
    WHERE $wallet IS NULL OR s.address CONTAINS $wallet OR r.address CONTAINS $wallet
    RETURN s.address AS sender, r.address AS receiver, t.value AS value, t.timestamp AS timestamp
    ORDER BY """ + sort_by + " " + order + """
    SKIP $offset LIMIT $limit
    """
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session() as session:
            result = session.run(query, wallet=wallet, offset=offset, limit=limit)
            return [record.values() for record in result]

THRESHOLD_LARGE_TX = 10000  # Ambang batas transaksi besar (ETH)

def detect_large_tx_for_wallet(wallet):
    """Deteksi transaksi besar terkait dengan wallet tertentu sebagai sender atau receiver."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Query untuk mendapatkan transaksi pertama kali di atas threshold untuk wallet tertentu
    cur.execute("""
        SELECT sender, receiver, value, timestamp
        FROM transactions t1
        WHERE value >= %s
        AND (sender = %s OR receiver = %s)
        AND timestamp = (
            SELECT MIN(timestamp) 
            FROM transactions t2
            WHERE t1.sender = t2.sender 
            AND t1.receiver = t2.receiver
        )
        ORDER BY timestamp ASC
    """, (THRESHOLD_LARGE_TX, wallet, wallet))

    anomalies = cur.fetchall()

    cur.close()
    conn.close()

    return anomalies

def get_first_large_tx_api(wallet_address: str):
    """
    Return list of the first “large” tx above threshold for this wallet.
    """
    anomalies = detect_large_tx_for_wallet(wallet_address)
    return [
        {
            "sender":      sender,
            "receiver":    receiver,
            "amount":      float(value),
            "timestamp":   int(ts.timestamp()),  # epoch seconds
        }
        for sender, receiver, value, ts in anomalies
    ]

def get_hourly_transaction_count(wallet):
    """Mengambil jumlah transaksi per 1 jam untuk wallet tertentu sebagai sender dan receiver."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Hitung jumlah transaksi sebagai sender per 1 jam
    cur.execute("""
        SELECT DATE_TRUNC('hour', timestamp) AS hour_bucket, COUNT(*) 
        FROM transactions
        WHERE sender = %s
        GROUP BY hour_bucket
        HAVING COUNT(*) > 50
        ORDER BY hour_bucket ASC
    """, (wallet,))

    sender_hourly_tx_counts = cur.fetchall()

    # Hitung jumlah transaksi sebagai receiver per 1 jam
    cur.execute("""
        SELECT DATE_TRUNC('hour', timestamp) AS hour_bucket, COUNT(*) 
        FROM transactions
        WHERE receiver = %s
        GROUP BY hour_bucket
        HAVING COUNT(*) > 50
        ORDER BY hour_bucket ASC
    """, (wallet,))

    receiver_hourly_tx_counts = cur.fetchall()

    cur.close()
    conn.close()

    return sender_hourly_tx_counts, receiver_hourly_tx_counts

def get_risky_interactions(wallet_address):
    """
    Mengambil daftar transaksi di mana wallet_address berinteraksi dengan alamat berisiko tinggi.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Cari semua alamat berisiko tinggi
    cur.execute("SELECT address FROM wallet_risk WHERE risk_profile = 'High Risk'")
    risky_addresses = {row[0] for row in cur.fetchall()}  # Set untuk pencarian cepat

    # Ambil semua transaksi wallet
    cur.execute("""
        SELECT sender, receiver, value, timestamp 
        FROM transactions 
        WHERE sender = %s OR receiver = %s
    """, (wallet_address, wallet_address))

    risky_interactions = []
    for tx in cur.fetchall():
        sender, receiver, value, timestamp = tx
        
        # Cek apakah wallet_address berinteraksi dengan alamat risiko tinggi
        if (sender == wallet_address and receiver in risky_addresses) or \
           (receiver == wallet_address and sender in risky_addresses):
            risky_interactions.append({
                "sender": sender,
                "receiver": receiver,
                "value": value,
                "timestamp": timestamp,
                "risk_source": receiver if sender == wallet_address else sender  # Alamat yang berisiko
            })

    cur.close()
    conn.close()
    return risky_interactions

def get_blacklist_interactions(wallet_address):
    """
    Mengambil daftar transaksi wallet_address dengan alamat yang masuk daftar blacklist (scam).
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Ambil semua address dari blacklist_addresses
    cur.execute("SELECT address FROM blacklist_addresses")
    blacklisted = {row[0] for row in cur.fetchall()}  # Gunakan set untuk performa

    # Ambil semua transaksi wallet tersebut
    cur.execute("""
        SELECT sender, receiver, value, timestamp 
        FROM transactions 
        WHERE sender = %s OR receiver = %s
    """, (wallet_address, wallet_address))

    blacklist_interactions = []
    for tx in cur.fetchall():
        sender, receiver, value, timestamp = tx

        # Cek apakah lawan transaksi adalah blacklist
        if (sender == wallet_address and receiver in blacklisted) or \
           (receiver == wallet_address and sender in blacklisted):
            blacklist_interactions.append({
                "sender": sender,
                "receiver": receiver,
                "value": value,
                "timestamp": timestamp,
                "blacklisted_party": receiver if sender == wallet_address else sender
            })

    cur.close()
    conn.close()
    return blacklist_interactions

def detect_recurring_transactions_raw(wallet_address):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp FROM transactions 
        WHERE sender = %s OR receiver = %s
        ORDER BY timestamp ASC
    """, (wallet_address, wallet_address))
    timestamps = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    if len(timestamps) < 5:
        return None  # terlalu sedikit

    dates = [datetime.fromtimestamp(ts.timestamp()).date() for ts in timestamps]
    diffs = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
    freq = Counter(diffs)

    if freq[1] >= len(dates) * 0.7:
        return "daily"
    if freq[7] >= len(dates) * 0.5:
        return "weekly"
    if any(freq[d] >= len(dates) * 0.3 for d in range(28, 32)):
        return "monthly"
    return None

def detect_repeated_value_transactions(wallet_address):
    """
    Mendeteksi transaksi dengan jumlah ETH yang sama lebih dari 10 kali ke alamat yang sama,
    dan mengelompokkannya dalam tabel berdasarkan pasangan sender-receiver.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Ambil transaksi wallet dari database
    cur.execute("""
        SELECT sender, receiver, value, timestamp FROM transactions 
        WHERE sender = %s OR receiver = %s
        ORDER BY timestamp ASC
    """, (wallet_address, wallet_address))

    transactions = cur.fetchall()
    cur.close()
    conn.close()

    if len(transactions) < 10:  # Jika transaksi terlalu sedikit, skip analisis
        return {}

    # Hitung jumlah transaksi dengan ETH yang sama antara sender-receiver yang sama
    value_counts = Counter((tx[0], tx[1], tx[2]) for tx in transactions)
    
    # Ambil pasangan sender-receiver dengan nilai ETH yang sama lebih dari 10 kali
    common_pairs = {key for key, count in value_counts.items() if count > 10}

    # Kelompokkan transaksi berdasarkan sender-receiver
    grouped_transactions = defaultdict(list)

    for tx in transactions:
        key = (tx[0], tx[1], tx[2])  # (sender, receiver, value)
        if key in common_pairs:
            grouped_transactions[(tx[0], tx[1], tx[2])].append({
                "sender": tx[0],
                "receiver": tx[1],
                "value": tx[2],
                "timestamp": tx[3]
            })

    return grouped_transactions  # Dictionary dengan kunci (sender, receiver, value)

def get_color(address):
    """Menghasilkan warna unik berdasarkan address"""
    hash_value = hashlib.md5(address.encode()).hexdigest()[:6]  # Ambil 6 karakter pertama dari hash MD5
    return f"#{hash_value}"  # Format warna HEX
   
def get_anomaly_transaction_count():
    """
    Menghitung total transaksi di tabel 'transactions' dengan is_anomaly = TRUE
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM transactions WHERE is_anomaly = TRUE;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"total_anomalies": int(count)}

def get_high_risk_address_count(threshold: float = 0.8):
    """
    Menghitung jumlah address di suspicious_addresses
    dengan risk_score >= threshold.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) 
        FROM suspicious_addresses 
        WHERE risk_score >= %s;
    """, (threshold,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"high_risk_addresses": int(count), "threshold": threshold}

def get_anomaly_cases(limit: int = 10):
    """
    Mengambil transaksi anomalous terbaru (ETH saja)
    dan membungkusnya sebagai AML Case.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT tx_hash, sender, value, timestamp
        FROM transactions
        WHERE is_anomaly = TRUE
        ORDER BY timestamp DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    cases = []
    for tx_hash, sender, value, ts in rows:
        cases.append({
            "case_id":     f"AML-ETH-{tx_hash[:8]}",   # ID unik berbasis hash
            "wallet":      sender,
            "entity_type": "Wallet",
            "crypto":      "ETH",                      # statis ETH
            "amount":      f"{value} ETH",
            "risk":        "High",                     # anomaly selalu High
            "status":      "Under Review",
            "date":        ts.date().isoformat()
        })
    return cases

def get_transaction_details(tx_hash: str):
    """
    Ambil detail satu transaksi berdasarkan tx_hash,
    termasuk flag is_anomaly dan profil risiko dari sender dan receiver.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.tx_hash,
               t.sender,
               t.receiver,
               t.value,
               t.timestamp,
               t.is_anomaly,
               sr.risk_score AS sender_risk_score,
               sr.risk_profile AS sender_risk_profile,
               rr.risk_score AS receiver_risk_score,
               rr.risk_profile AS receiver_risk_profile
        FROM transactions t
        LEFT JOIN wallet_risk sr ON t.sender = sr.address
        LEFT JOIN wallet_risk rr ON t.receiver = rr.address
        WHERE t.tx_hash = %s
    """, (tx_hash,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return None

    (
        tx_hash, sender, receiver, value, ts, is_anom,
        s_risk_score, s_risk_cat,
        r_risk_score, r_risk_cat
    ) = row

    return {
        "tx_hash": tx_hash,
        "sender": sender,
        "receiver": receiver,
        "amount": f"{value} ETH",
        "crypto": "ETH",
        "timestamp": ts.isoformat(),
        "is_anomaly": bool(is_anom),
        "sender_profile": {
            "risk_score": s_risk_score,
            "risk_profile": s_risk_cat,
        },
        "receiver_profile": {
            "risk_score": r_risk_score,
            "risk_profile": r_risk_cat,
        }
    }
