from ..database import get_db_connection
from neo4j import GraphDatabase
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
from psycopg2.extras import RealDictCursor

# =========================
# Konfigurasi koneksi Neo4j
# =========================
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

# Driver dibuat sekali (reuse)
neo4j_conn = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

# Pemetaan case_type -> enum/text di tabel cases
CASE_TYPE_MAP = {
    'wallet': 'suspicious wallet',
    'tx': 'anomaly transaction',
    'transaction': 'anomaly transaction'
}

# =======================================================================
# Utilitas
# =======================================================================
def _table_has_column(conn, table_name: str, column_name: str) -> bool:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
              AND column_name = %s
            LIMIT 1
        """, (table_name, column_name))
        return cur.fetchone() is not None

def _normalize_to_eth(value_numeric):
    """
    Heuristik normalisasi:
    - Jika value sangat besar (diduga wei), konversi ke ETH (/1e18).
    - Jika tidak, anggap sudah ETH.
    """
    return (value_numeric / 1e18) if value_numeric and value_numeric > 1e12 else float(value_numeric or 0.0)

def get_color(address: str) -> str:
    """Menghasilkan warna unik berdasarkan address (HEX)."""
    hash_value = hashlib.md5(address.encode()).hexdigest()[:6]
    return f"#{hash_value}"

# =======================================================================
# Analitik & Graph
# =======================================================================
def get_transaction_analysis(wallet_address: str):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT timestamp, value 
            FROM transactions 
            WHERE sender = %s OR receiver = %s
            ORDER BY timestamp ASC
        """, (wallet_address, wallet_address))
        data = cur.fetchall()

    timestamps = [row[0].strftime("%Y-%m-%d %H:%M:%S") for row in data]
    values = [row[1] for row in data]
    return timestamps, values

def get_transitive_risk_graph(wallet_address: str, max_hops: int = 3, limit: int = 50):
    """
    Kembalikan list of nodes (id,color), edges (from,to,label), dan legend,
    hanya berdasarkan blacklist_source → target wallet dalam max_hops.
    """
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
        edges = []

        # node pusat (target)
        nodes_map[wallet_address] = {"id": wallet_address, "color": "#0d6efd"}

        for r in records:
            src = r["blacklist_source"]
            hops = r["hops"]

            if src not in nodes_map:
                nodes_map[src] = {"id": src, "color": "#dc3545"}

            edges.append({
                "from": src,
                "to": wallet_address,
                "label": f"{hops} hop"
            })

    nodes = list(nodes_map.values())
    color_legend = {n["id"]: n["color"] for n in nodes}
    return nodes, edges, color_legend

def get_transactions_from_neo4j(wallet=None, sort_by="timestamp", order="desc", limit=10, offset=0):
    """Mengambil transaksi dari Neo4j dengan filter dan sorting (whitelist kolom)."""
    # NOTE: whitelist untuk cegah injeksi via ORDER BY
    sort_whitelist = {"timestamp", "value"}
    order_whitelist = {"asc", "desc"}

    sort_by = sort_by.lower()
    order = order.lower()
    if sort_by not in sort_whitelist:
        sort_by = "timestamp"
    if order not in order_whitelist:
        order = "desc"

    query = f"""
    MATCH (s:Wallet)-[t:SEND]->(r:Wallet)
    WHERE $wallet IS NULL OR s.address CONTAINS $wallet OR r.address CONTAINS $wallet
    RETURN s.address AS sender, r.address AS receiver, t.value AS value, t.timestamp AS timestamp
    ORDER BY {sort_by} {order}
    SKIP $offset LIMIT $limit
    """

    with neo4j_conn.session() as session:
        result = session.run(query, wallet=wallet, offset=offset, limit=limit)
        return [record.values() for record in result]

# =======================================================================
# Heuristik & Deteksi
# =======================================================================
THRESHOLD_LARGE_TX_ETH = 10000.0  # ambang dalam ETH

def detect_large_tx_for_wallet(wallet: str):
    """
    Deteksi transaksi pertama (per pasangan counterparty) yang >= threshold ETH
    untuk wallet sebagai sender atau receiver.
    """
    # NOTE: versi sebelumnya mengambil "first ever between pair" alih-alih
    # "first >= threshold". Kita normalisasi ke ETH dulu, lalu filter.
    sql = """
    WITH tx AS (
        SELECT
            sender,
            receiver,
            CASE
              WHEN value > 1e12 THEN (value / 1e18::numeric)
              ELSE value::numeric
            END AS value_eth,
            timestamp
        FROM transactions
        WHERE sender = %(w)s OR receiver = %(w)s
    ),
    big AS (
        SELECT
            sender, receiver, value_eth, timestamp,
            ROW_NUMBER() OVER (
                PARTITION BY LEAST(sender, receiver), GREATEST(sender, receiver)
                ORDER BY timestamp ASC
            ) AS rn
        FROM tx
        WHERE value_eth >= %(thr)s
    )
    SELECT sender, receiver, value_eth, timestamp
    FROM big
    WHERE rn = 1
    ORDER BY timestamp ASC;
    """

    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, {"w": wallet, "thr": THRESHOLD_LARGE_TX_ETH})
        return cur.fetchall()

def get_first_large_tx_api(wallet_address: str):
    rows = detect_large_tx_for_wallet(wallet_address)
    return [
        {
            "sender":    s,
            "receiver":  r,
            "amount":    float(v_eth),
            "timestamp": int(ts.timestamp()),
        }
        for (s, r, v_eth, ts) in rows
    ]

def get_hourly_transaction_count(wallet: str):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT DATE_TRUNC('hour', timestamp) AS hour_bucket, COUNT(*) 
            FROM transactions
            WHERE sender = %s
            GROUP BY hour_bucket
            HAVING COUNT(*) > 50
            ORDER BY hour_bucket ASC
        """, (wallet,))
        sender_hourly = cur.fetchall()

        cur.execute("""
            SELECT DATE_TRUNC('hour', timestamp) AS hour_bucket, COUNT(*) 
            FROM transactions
            WHERE receiver = %s
            GROUP BY hour_bucket
            HAVING COUNT(*) > 50
            ORDER BY hour_bucket ASC
        """, (wallet,))
        receiver_hourly = cur.fetchall()

    return sender_hourly, receiver_hourly

def get_risky_interactions(wallet_address: str):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT address FROM wallet_risk WHERE risk_profile = 'High Risk'")
        risky_addresses = {row[0] for row in cur.fetchall()}

        cur.execute("""
            SELECT sender, receiver, value, timestamp 
            FROM transactions 
            WHERE sender = %s OR receiver = %s
        """, (wallet_address, wallet_address))

        risky_interactions = []
        for sender, receiver, value, timestamp in cur.fetchall():
            if (sender == wallet_address and receiver in risky_addresses) or \
               (receiver == wallet_address and sender in risky_addresses):
                risky_interactions.append({
                    "sender": sender,
                    "receiver": receiver,
                    "value": value,
                    "timestamp": timestamp,
                    "risk_source": receiver if sender == wallet_address else sender
                })

    return risky_interactions

def get_blacklist_interactions(wallet_address: str):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT address FROM blacklist_addresses")
        blacklisted = {row[0] for row in cur.fetchall()}

        cur.execute("""
            SELECT sender, receiver, value, timestamp 
            FROM transactions 
            WHERE sender = %s OR receiver = %s
        """, (wallet_address, wallet_address))

        interactions = []
        for sender, receiver, value, timestamp in cur.fetchall():
            if (sender == wallet_address and receiver in blacklisted) or \
               (receiver == wallet_address and sender in blacklisted):
                interactions.append({
                    "sender": sender,
                    "receiver": receiver,
                    "value": value,
                    "timestamp": timestamp,
                    "blacklisted_party": receiver if sender == wallet_address else sender
                })
    return interactions

def detect_recurring_transactions_raw(wallet_address: str):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT timestamp FROM transactions 
            WHERE sender = %s OR receiver = %s
            ORDER BY timestamp ASC
        """, (wallet_address, wallet_address))
        timestamps = [row[0] for row in cur.fetchall()]

    if len(timestamps) < 5:
        return None

    # NOTE: cukup gunakan ts.date() (hindari round-trip .timestamp() → fromtimestamp())
    dates = [ts.date() for ts in timestamps]
    diffs = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
    freq = Counter(diffs)

    if freq[1] >= len(dates) * 0.7:
        return "daily"
    if freq[7] >= len(dates) * 0.5:
        return "weekly"
    if any(freq[d] >= len(dates) * 0.3 for d in range(28, 32)):
        return "monthly"
    return None

def detect_repeated_value_transactions(wallet_address: str):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT sender, receiver, value, timestamp FROM transactions 
            WHERE sender = %s OR receiver = %s
            ORDER BY timestamp ASC
        """, (wallet_address, wallet_address))
        transactions = cur.fetchall()

    if len(transactions) < 10:
        return {}

    value_counts = Counter((tx[0], tx[1], tx[2]) for tx in transactions)
    common_pairs = {key for key, count in value_counts.items() if count > 10}

    grouped = defaultdict(list)
    for s, r, v, ts in transactions:
        key = (s, r, v)
        if key in common_pairs:
            grouped[(s, r, v)].append({
                "sender": s,
                "receiver": r,
                "value": v,
                "timestamp": ts
            })
    return grouped

def get_anomaly_transaction_count():
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM anomalies a
            LEFT JOIN cases c
                   ON c.case_type::text = %s
                  AND lower(c.reference_id) = lower(a.tx_hash)
            WHERE a.tx_hash IS NOT NULL
              AND c.id IS NULL
        """, (CASE_TYPE_MAP['transaction'],))
        return {"count": cur.fetchone()[0]}

def get_high_risk_address_count(threshold: float = 0.8):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) 
            FROM suspicious_addresses 
            WHERE risk_score >= %s;
        """, (threshold,))
        count = cur.fetchone()[0]
    return {"high_risk_addresses": int(count), "threshold": threshold}

def get_anomaly_cases(limit: int = 10):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT tx_hash, sender, value, timestamp
            FROM transactions
            WHERE is_anomaly = TRUE
            ORDER BY timestamp DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()

    cases = []
    for tx_hash, sender, value, ts in rows:
        cases.append({
            "case_id":     f"AML-ETH-{tx_hash[:8]}",
            "wallet":      sender,
            "entity_type": "Wallet",
            "crypto":      "ETH",
            "amount":      f"{value} ETH",
            "risk":        "High",
            "status":      "Under Review",
            "date":        ts.date().isoformat()
        })
    return cases

def get_transaction_details(tx_hash: str):
    with get_db_connection() as conn, conn.cursor() as cur:
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

    if not row:
        return None

    (tx_hash, sender, receiver, value, ts, is_anom,
     s_risk_score, s_risk_cat,
     r_risk_score, r_risk_cat) = row

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

def get_anomaly_transactions(limit=100, offset=0):
    """
    Ambil daftar anomaly transaksi dari tabel anomalies (kolom detector/reason),
    lengkapi dengan detail transaksi jika tersedia.
    - Hanya anomaly dengan a.tx_hash IS NOT NULL (tipe transaksi).
    - Exclude yang sudah dibuat case (cases.case_type='anomaly transaction' & reference_id=tx_hash).
    """
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Cek kolom opsional di transactions agar aman di skema lama/baru
        has_block_time = _table_has_column(conn, "transactions", "block_time")

        time_expr = "COALESCE(t.timestamp, t.block_time, a.created_at)" if has_block_time \
                    else "COALESCE(t.timestamp, a.created_at)"

        cur.execute(f"""
            SELECT
                a.tx_hash,
                t.sender,
                t.receiver,
                t.value,
                {time_expr}         AS timestamp,
                a.detector,
                a.reason
            FROM anomalies a
            LEFT JOIN transactions t
                   ON lower(t.tx_hash) = lower(a.tx_hash)
            LEFT JOIN cases c
                   ON c.case_type::text = %s
                  AND lower(c.reference_id) = lower(a.tx_hash)
            WHERE a.tx_hash IS NOT NULL
              AND c.id IS NULL
            ORDER BY {time_expr} DESC NULLS LAST
            LIMIT %s OFFSET %s
        """, (CASE_TYPE_MAP['transaction'], limit, offset))
        return cur.fetchall()

def get_blacklisted_wallets(limit=100, offset=0):
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT
                b.address, b.source, b.category, b.reason, b.added_on
            FROM blacklist_addresses b
            LEFT JOIN cases c
              ON c.case_type::text = %s
             AND lower(c.reference_id) = lower(b.address)
            WHERE c.id IS NULL
            ORDER BY b.added_on DESC NULLS LAST
            LIMIT %s OFFSET %s
        """, (CASE_TYPE_MAP['wallet'], limit, offset))
        return cur.fetchall()
    
def get_blacklisted_wallets_count():
    """Hitung jumlah wallet di blacklist yang BELUM dibuat case."""
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM blacklist_addresses b
            LEFT JOIN cases c
                   ON c.case_type::text = %s
                  AND lower(c.reference_id) = lower(b.address)
            WHERE c.id IS NULL
        """, (CASE_TYPE_MAP['wallet'],))
        return {"count": cur.fetchone()[0]}

def get_suspicious_summary():
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM transactions WHERE is_anomaly = TRUE;")
        total = cur.fetchone()[0] or 0

        cur.execute("""
            SELECT 
              COUNT(*) FILTER (WHERE timestamp::date = CURRENT_DATE) AS today,
              COUNT(*) FILTER (WHERE timestamp::date = CURRENT_DATE - INTERVAL '1 day') AS yesterday
            FROM transactions
            WHERE is_anomaly = TRUE;
        """)
        row = cur.fetchone()
        today = (row[0] or 0) if row else 0
        yesterday = (row[1] or 0) if row else 0

        cur.execute("""
            SELECT 
              SUM(CASE WHEN sender LIKE '0x%%' OR receiver LIKE '0x%%' THEN 1 ELSE 0 END) AS eth,
              SUM(CASE WHEN sender LIKE '0x%%' OR receiver LIKE '0x%%' THEN 0 ELSE 1 END) AS btc
            FROM transactions
            WHERE is_anomaly = TRUE;
        """)
        eth, btc = cur.fetchone() or (0, 0)

    delta_pct = None
    direction = 'flat'
    if yesterday > 0:
        diff = (today - yesterday) / yesterday
        delta_pct = round(diff, 4)
        direction = 'up' if diff >= 0 else 'down'

    return {
        "total": int(total),
        "by_chain": {"ETH": int(eth or 0), "BTC": int(btc or 0)},
        "today": int(today),
        "yesterday": int(yesterday),
        "delta_pct": delta_pct,
        "direction": direction
    }

def get_wallet_risk_metrics(address: str, high_value_eth: float = 10.0, risk_score_cutoff: int = 70):
    """
    Metrik 1 wallet:
      - Persentase anomali (zscore |value_eth| >= 3)
      - High-value (>= high_value_eth)
      - Counterparty high-risk
      - Counterparty blacklisted
    """
    conn = get_db_connection()

    has_risk_score = _table_has_column(conn, "blacklist_addresses", "risk_score")
    has_severity   = _table_has_column(conn, "blacklist_addresses", "severity")

    sql = f"""
    WITH tx AS (
        SELECT
            t.tx_hash,
            t.sender,
            t.receiver,
            CASE
              WHEN t.value > 1e12 THEN t.value / 1e18::numeric
              ELSE t.value::numeric
            END AS value_eth
        FROM transactions t
        WHERE lower(t.sender)  = lower(%(addr)s)
           OR lower(t.receiver)= lower(%(addr)s)
    ),
    total AS (
        SELECT COUNT(*) AS total_tx FROM tx
    ),
    dist AS (
        SELECT
            value_eth,
            CASE
              WHEN STDDEV_POP(value_eth) OVER () = 0 THEN NULL
              ELSE (value_eth - AVG(value_eth) OVER ()) / NULLIF(STDDEV_POP(value_eth) OVER (), 0)
            END AS zscore
        FROM tx
    ),
    anomaly AS (
        SELECT COUNT(*) AS anomaly_cnt
        FROM dist
        WHERE zscore IS NOT NULL AND ABS(zscore) >= 3
    ),
    high_value AS (
        SELECT COUNT(*) AS high_value_cnt
        FROM tx
        WHERE value_eth >= %(high_value_eth)s
    ),
    counterparty AS (
        SELECT
          CASE WHEN lower(sender)=lower(%(addr)s) THEN receiver ELSE sender END AS counterparty
        FROM tx
    ),
    joined AS (
        SELECT
          c.counterparty,
          bl.address IS NOT NULL AS is_blacklisted
          {", bl.risk_score" if has_risk_score else ""}
          {", bl.severity"   if has_severity   else ""}
        FROM counterparty c
        LEFT JOIN blacklist_addresses bl
          ON lower(bl.address) = lower(c.counterparty)
    ),
    risk_counts AS (
        SELECT
          COUNT(*) FILTER (WHERE is_blacklisted) AS blacklisted_cnt,
          COUNT(*) FILTER (
            WHERE
              {(
                 "risk_score >= %(risk_cutoff)s"
               ) if has_risk_score else (
                 "COALESCE(NULLIF(LOWER(severity),'') IN ('high','critical'), false)"
               ) if has_severity else (
                 "is_blacklisted"
               )}
          ) AS risky_cnt
        FROM joined
    )
    SELECT
      (SELECT total_tx        FROM total)        AS total_tx,
      (SELECT anomaly_cnt     FROM anomaly)      AS anomaly_cnt,
      (SELECT high_value_cnt  FROM high_value)   AS high_value_cnt,
      (SELECT risky_cnt       FROM risk_counts)  AS risky_cnt,
      (SELECT blacklisted_cnt FROM risk_counts)  AS blacklisted_cnt;
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, {
            "addr": address,
            "high_value_eth": high_value_eth,
            "risk_cutoff": risk_score_cutoff,
        })
        row = cur.fetchone() or {}

    total = int(row.get("total_tx") or 0)
    anomaly_cnt     = int(row.get("anomaly_cnt") or 0)
    high_value_cnt  = int(row.get("high_value_cnt") or 0)
    risky_cnt       = int(row.get("risky_cnt") or 0)
    blacklisted_cnt = int(row.get("blacklisted_cnt") or 0)

    def pct(x: int) -> float:
        return 0.0 if total == 0 else round((x / total) * 100.0, 2)

    return {
        "address": address,
        "totalTx": total,
        "anomaly": {
            "count": anomaly_cnt,
            "percent": pct(anomaly_cnt),
            "method": "zscore>=3 on value_eth"
        },
        "highValue": {
            "count": high_value_cnt,
            "percent": pct(high_value_cnt),
            "thresholdEth": float(high_value_eth)
        },
        "riskyCounterparty": {
            "count": risky_cnt,
            "percent": pct(risky_cnt),
            "note": (
                "by blacklist.risk_score >= cutoff"
                if has_risk_score else
                ("by blacklist.severity in (High,Critical)" if has_severity else "fallback: equals blacklisted")
            )
        },
        "blacklistedCounterparty": {
            "count": blacklisted_cnt,
            "percent": pct(blacklisted_cnt)
        }
    }

def get_transactions_for_wallet(address: str, sort_by="timestamp", order="desc", page=1, per_page=10):
    valid_columns = ['value', 'timestamp']
    if sort_by not in valid_columns:
        sort_by = 'timestamp'
    order_query = "ASC" if str(order).lower() == "asc" else "DESC"
    offset = max(0, (page - 1)) * per_page

    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT sender, receiver, value, timestamp, is_anomaly
            FROM transactions
            WHERE sender ILIKE %s OR receiver ILIKE %s
            ORDER BY {sort_by} {order_query}
            LIMIT %s OFFSET %s
        """, (f"%{address}%", f"%{address}%", per_page, offset))
        transactions = cur.fetchall()

        cur.execute("""
            SELECT COUNT(*) AS count
            FROM transactions
            WHERE sender ILIKE %s OR receiver ILIKE %s
        """, (f"%{address}%", f"%{address}%"))
        total_rows = cur.fetchone()["count"]

    return {
        "transactions": transactions,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_rows": total_rows,
            "total_pages": (total_rows // per_page) + (1 if total_rows % per_page else 0)
        }
    }