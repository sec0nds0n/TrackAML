from ..database import get_db_connection
from ..services.risk_analysis import calculate_wallet_risk, fetch_transactions_from_db
from ..services.neo4j_sync import is_neo4j_running, migrate_transactions, label_blacklisted_wallets
from ..services.kyc_service import is_wallet_blacklisted, get_top_transactions, get_top_receivers, get_top_senders
from decimal import Decimal
from psycopg2.extras import RealDictCursor

import requests
import pandas as pd
import numpy as np
import joblib
import os
import psycopg2
import psycopg2.extras

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
MODEL_DIR = os.path.join(BASE_DIR, 'models')

IF_MODEL_PATH   = os.path.join(MODEL_DIR, 'isolation_forest_best_model.pkl')
XGB_MODEL_PATH  = os.path.join(MODEL_DIR, 'model_xgboost_aml.pkl')
SCALER_PATH     = os.path.join(MODEL_DIR, 'scaler_if.pkl')
SCALER_XGB_PATH = os.path.join(MODEL_DIR, 'scaler_xgb.pkl')

# Load model deteksi anomali
model       = joblib.load(IF_MODEL_PATH)
xgb_model   = joblib.load(XGB_MODEL_PATH)
scaler      = joblib.load(SCALER_PATH)
scaler_xgb  = joblib.load(SCALER_XGB_PATH)

def fetch_transactions_df(wallet_address):
    conn = get_db_connection()
    query = """
        SELECT tx_hash, sender, receiver, value, timestamp
        FROM transactions
        WHERE sender = %s OR receiver = %s
        ORDER BY timestamp ASC
    """
    df = pd.read_sql(query, conn, params=(wallet_address, wallet_address))
    conn.close()
    return df

def fetch_all_transactions(wallet_address: str):
    conn = get_db_connection()
    # Gunakan DictCursor agar kita bisa akses kolom by name
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT
            tx_hash,
            sender,
            receiver,
            value,
            EXTRACT(EPOCH FROM timestamp) AS ts_epoch,
            is_anomaly
        FROM transactions
        WHERE sender = %s OR receiver = %s
        ORDER BY timestamp ASC
    """, (wallet_address, wallet_address))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Bangun JSON-friendly list of dict
    return [
        {
            "tx_hash":       r["tx_hash"],
            "type":          "sent" if r["sender"] == wallet_address else "received",
            "amount":        float(r["value"]),
            "crypto":        "ETH",
            "counterparty":  (r["receiver"] 
                              if r["sender"] == wallet_address 
                              else r["sender"]),
            "timestamp":     int(r["ts_epoch"]),
            "is_anomaly":    bool(r["is_anomaly"])
        }
        for r in rows
    ]

def extract_wallet_features(df, wallet_address):
    # Pastikan kolom timestamp sebagai datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Fitur waktu: jam dan hari
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)

    # Transformasi nilai transaksi
    df['value'] = df['value'].clip(lower=0)
    df['log_value'] = np.log1p(df['value'])

    # Flag transaksi besar berdasarkan kuantil 95%
    threshold_95 = df['value'].quantile(0.95)
    df['is_large_global'] = (df['value'] > threshold_95).astype(int)

    # Jumlah transaksi per sender/receiver
    sender_counts = df['sender'].value_counts().to_dict()
    receiver_counts = df['receiver'].value_counts().to_dict()
    df['sender_tx_count'] = df['sender'].map(sender_counts)
    df['receiver_tx_count'] = df['receiver'].map(receiver_counts)

    # Frekuensi pasangan.sender-receiver
    pair_counts = df.groupby(['sender', 'receiver']).size().to_dict()
    df['tx_pair_freq'] = df.apply(
        lambda row: pair_counts.get((row['sender'], row['receiver']), 0),
        axis=1
    )

    # Waktu antar transaksi per sender
    df.sort_values(['sender', 'timestamp'], inplace=True)
    df['prev_time'] = df.groupby('sender')['timestamp'].shift(1)
    df['inter_time'] = (df['timestamp'] - df['prev_time']).dt.total_seconds()
    df['inter_time'] = df['inter_time'].fillna(df['inter_time'].median())

    # Hitung kemunculan nilai yang sama per sender
    df['same_value_count'] = df.groupby(['sender', 'value'])['value'].transform('count')

    # Pilih kolom fitur sesuai model
    feature_cols = [
        'log_value', 'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
        'is_large_global', 'sender_tx_count', 'receiver_tx_count',
        'tx_pair_freq', 'inter_time', 'same_value_count'
    ]
    features_df = df[feature_cols].copy()
    features_df = features_df.fillna(features_df.median())
    return features_df

def prepare_features(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek

    df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)

    df['value'] = df['value'].clip(lower=0)
    df['log_value'] = np.log1p(df['value'])

    threshold_95 = df['value'].quantile(0.95)
    df['is_large_global'] = (df['value'] > threshold_95).astype(int)

    sender_counts = df['sender'].value_counts().to_dict()
    receiver_counts = df['receiver'].value_counts().to_dict()
    df['sender_tx_count'] = df['sender'].map(sender_counts)
    df['receiver_tx_count'] = df['receiver'].map(receiver_counts)

    pair_counts = df.groupby(['sender', 'receiver']).size().to_dict()
    df['tx_pair_freq'] = df.apply(lambda row: pair_counts.get((row['sender'], row['receiver']), 0), axis=1)

    df.sort_values(['sender', 'timestamp'], inplace=True)
    df['prev_time'] = df.groupby('sender')['timestamp'].shift(1)
    df['inter_time'] = (df['timestamp'] - df['prev_time']).dt.total_seconds()
    df['inter_time'] = df['inter_time'].fillna(df['inter_time'].median())

    df['same_value_count'] = df.groupby(['sender', 'value'])['value'].transform('count')

    return df[[
        'log_value', 'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
        'is_large_global', 'sender_tx_count', 'receiver_tx_count',
        'tx_pair_freq', 'inter_time', 'same_value_count'
    ]]

def detect_anomalies(df):
    features = prepare_features(df)
    features_scaled = pd.DataFrame(scaler.transform(features), columns=features.columns)
    df['is_anomaly'] = model.predict(features_scaled)
    df['is_anomaly'] = df['is_anomaly'].apply(lambda x: 1 if x == -1 else 0)
    return df

def fetch_and_analyze_wallet(wallet_address):
    conn = get_db_connection()
    cur = conn.cursor()

    # Ambil transaksi dari Etherscan
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet_address}&sort=asc&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url).json()

    if response.get("status") != "1" or "result" not in response:
        cur.close()
        conn.close()
        return False, "Gagal mengambil data dari Etherscan."

    transactions = response["result"]
    inserted_tx = []

    for tx in transactions:
        tx_hash = tx["hash"]
        sender = tx["from"]
        receiver = tx["to"]
        value = int(tx["value"]) / 1e18
        timestamp = tx["timeStamp"]

        cur.execute("""
            INSERT INTO transactions (tx_hash, sender, receiver, value, timestamp)
            VALUES (%s, %s, %s, %s, TO_TIMESTAMP(%s))
            ON CONFLICT (tx_hash) DO NOTHING
        """, (tx_hash, sender, receiver, value, timestamp))

        inserted_tx.append({
            "tx_hash": tx_hash,
            "sender": sender,
            "receiver": receiver,
            "value": value,
            "timestamp": pd.to_datetime(int(timestamp), unit='s')
        })

    if inserted_tx:
        df_new = pd.DataFrame(inserted_tx)
        df_new = detect_anomalies(df_new)

        for _, row in df_new.iterrows():
            cur.execute("""
                UPDATE transactions SET is_anomaly = %s::boolean WHERE tx_hash = %s
            """, (row['is_anomaly'], row['tx_hash']))

    # Simpan wallet ke wallet_history
    cur.execute("""
        INSERT INTO wallet_history (address, queried_at)
        VALUES (%s, NOW())
        ON CONFLICT (address) DO UPDATE SET queried_at = NOW()
    """, (wallet_address,))

    conn.commit()
    cur.close()
    conn.close()
    return True, "Data transaksi berhasil diambil dan dianalisis."

def calculate_risk_all_logic():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT address FROM wallet_history")
    all_wallets = {row[0] for row in cur.fetchall()}

    cur.execute("SELECT address FROM wallet_risk")
    wallets_with_risk = {row[0] for row in cur.fetchall()}

    wallets_to_process = list(all_wallets - wallets_with_risk)

    count = 0
    for wallet_address in wallets_to_process:
        transactions = fetch_transactions_from_db(wallet_address)
        if transactions:
            risk_profile, risk_score = calculate_wallet_risk(wallet_address)

            cur.execute("""
                INSERT INTO wallet_risk (address, risk_score, risk_profile, last_updated)
                VALUES (%s, %s, %s, NOW())
            """, (wallet_address, risk_score, risk_profile))
            count += 1

    conn.commit()
    cur.close()
    conn.close()
    return count

def update_all_wallets_logic():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT address FROM wallet_history")
    wallets = cur.fetchall()

    success_count = 0
    fail_count = 0

    for (wallet_address,) in wallets:
        try:
            url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet_address}&sort=asc&apikey={ETHERSCAN_API_KEY}"
            response = requests.get(url).json()

            if response.get("status") != "1" or "result" not in response:
                fail_count += 1
                continue

            transactions = response["result"]

            for tx in transactions:
                tx_hash = tx["hash"]
                sender = tx["from"]
                receiver = tx["to"]
                value = int(tx["value"]) / 1e18
                timestamp = tx["timeStamp"]

                cur.execute("""
                    INSERT INTO transactions (tx_hash, sender, receiver, value, timestamp)
                    VALUES (%s, %s, %s, %s, TO_TIMESTAMP(%s))
                    ON CONFLICT (tx_hash) DO NOTHING
                """, (tx_hash, sender, receiver, value, timestamp))
                
            # klasifikasi dan blacklist
            df_tx = fetch_transactions_df(wallet_address)
            if not df_tx.empty:
                features_df = extract_wallet_features(df_tx, wallet_address)
                scaled = scaler_xgb.transform(features_df)
                prediction = xgb_model.predict(scaled)[0]
                if prediction == 1:
                    cur.execute("""
                        INSERT INTO blacklist_addresses (address, source, reason, added_on, category)
                        VALUES (%s, %s, %s, NOW(), %s)
                        ON CONFLICT (address) DO NOTHING
                    """, (wallet_address, 'ML-XGBoost', 'Detected as suspicious wallet by ML model', 'suspicious'))

            # update queried_at
            cur.execute("""
                UPDATE wallet_history
                SET queried_at = NOW()
                WHERE address = %s
            """, (wallet_address,))
            conn.commit()
            success_count += 1
            
        except Exception as e:
            print(f"Error saat update {wallet_address}: {e}")
            fail_count += 1
            conn.rollback()

    cur.close()
    conn.close()

    return success_count, fail_count

def sync_database_logic():
    if not is_neo4j_running():
        return False
    migrate_transactions()
    return True

def get_wallet_kyc(wallet_address):
    conn = get_db_connection()
    cur = conn.cursor()

    # Total ETH yang diterima oleh wallet
    cur.execute("""
        SELECT COALESCE(SUM(value), 0) 
        FROM transactions 
        WHERE receiver = %s
    """, (wallet_address,))
    total_received = cur.fetchone()[0]

    # Total ETH yang dikirim oleh wallet
    cur.execute("""
        SELECT COALESCE(SUM(value), 0) 
        FROM transactions 
        WHERE sender = %s
    """, (wallet_address,))
    total_sent = cur.fetchone()[0]

    # Saldo = Total diterima - Total dikirim
    balance = total_received - total_sent

    # Transaksi pertama berdasarkan timestamp
    cur.execute("""
        SELECT sender, receiver, value, timestamp 
        FROM transactions 
        WHERE sender = %s OR receiver = %s
        ORDER BY timestamp ASC LIMIT 1
    """, (wallet_address, wallet_address))
    first_tx = cur.fetchone()

    # Transaksi terakhir berdasarkan timestamp
    cur.execute("""
        SELECT sender, receiver, value, timestamp 
        FROM transactions 
        WHERE sender = %s OR receiver = %s
        ORDER BY timestamp DESC LIMIT 1
    """, (wallet_address, wallet_address))
    last_tx = cur.fetchone()

    cur.execute("""
        SELECT risk_score, risk_profile
        FROM wallet_risk
        WHERE address = %s
    """, (wallet_address,))
    risk_row = cur.fetchone()
    if risk_row:
        risk_score, risk_profile = risk_row
    else:
        risk_score = None
        risk_profile = "Unknown"
    cur.close()
    conn.close()

    # Build summary
    summary = {
        "balance": balance,
        "total_received": total_received,
        "total_sent": total_sent,
        "first_transaction": {
            "sender": first_tx[0],
            "receiver": first_tx[1],
            "amount": f"{first_tx[2]} ETH",
            "timestamp": first_tx[3].isoformat()
        } if first_tx else None,
        "last_transaction": {
            "sender": last_tx[0],
            "receiver": last_tx[1],
            "amount": f"{last_tx[2]} ETH",
            "timestamp": last_tx[3].isoformat()
        } if last_tx else None,
        
        "top_transactions": get_top_transactions(wallet_address),
        "top_receivers": get_top_receivers(wallet_address),
        "top_senders": get_top_senders(wallet_address),
        "blacklist_info": is_wallet_blacklisted(wallet_address),
        "risk_profile": {
            "risk_score": risk_score,
            "risk_profile": risk_profile
        }
    }

    return summary

def _to_float(x):
    try:
        return float(x) if x is not None else 0.0
    except Exception:
        return 0.0

def _row_to_tx_dict(row):
    """Konversi row transaksi (bisa None) ke dict untuk frontend."""
    if not row:
        return {
            "txHash": None,
            "sender": None,
            "receiver": None,
            "value": None,        # angka (ETH) atau None
            "timestamp": None,    # ISO8601 atau None
        }
    return {
        "txHash": row.get("tx_hash"),
        "sender": row.get("sender"),
        "receiver": row.get("receiver"),
        "value": _to_float(row.get("value")),
        "timestamp": row.get("timestamp").isoformat() if row.get("timestamp") else None,
    }

def get_wallet_balance_stats(wallet_address: str) -> dict:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            WITH filtered AS (
                SELECT *
                FROM transactions
                WHERE sender = %s OR receiver = %s
            ),
            agg AS (
                SELECT
                    COALESCE(SUM(CASE WHEN t.receiver = %s THEN t.value ELSE 0 END), 0) AS total_received,
                    COALESCE(SUM(CASE WHEN t.sender   = %s THEN t.value ELSE 0 END), 0) AS total_sent,
                    COUNT(*) AS transaction_count,
                    COUNT(DISTINCT CASE
                        WHEN t.sender = %s THEN t.receiver
                        WHEN t.receiver = %s THEN t.sender
                    END) AS unique_counterparties
                FROM filtered t
            ),
            first_tx AS (
                SELECT tx_hash, sender, receiver, value, timestamp
                FROM filtered
                ORDER BY timestamp ASC, tx_hash ASC
                LIMIT 1
            ),
            last_tx AS (
                SELECT tx_hash, sender, receiver, value, timestamp
                FROM filtered
                ORDER BY timestamp DESC, tx_hash DESC
                LIMIT 1
            )
            SELECT
                agg.total_received,
                agg.total_sent,
                agg.transaction_count,
                agg.unique_counterparties,

                first_tx.tx_hash   AS first_tx_hash,
                first_tx.sender    AS first_tx_sender,
                first_tx.receiver  AS first_tx_receiver,
                first_tx.value     AS first_tx_value,
                first_tx.timestamp AS first_tx_timestamp,

                last_tx.tx_hash    AS last_tx_hash,
                last_tx.sender     AS last_tx_sender,
                last_tx.receiver   AS last_tx_receiver,
                last_tx.value      AS last_tx_value,
                last_tx.timestamp  AS last_tx_timestamp
            FROM agg
            LEFT JOIN first_tx ON TRUE
            LEFT JOIN last_tx  ON TRUE
        """, (
            wallet_address, wallet_address,  # filtered
            wallet_address,                  # total_received
            wallet_address,                  # total_sent
            wallet_address, wallet_address,  # unique counterparties
        ))

        agg = cur.fetchone() or {}

        total_received = _to_float(agg.get("total_received"))
        total_sent     = _to_float(agg.get("total_sent"))
        balance        = total_received - total_sent

        first_row = {
            "tx_hash":  agg.get("first_tx_hash"),
            "sender":   agg.get("first_tx_sender"),
            "receiver": agg.get("first_tx_receiver"),
            "value":    agg.get("first_tx_value"),
            "timestamp":agg.get("first_tx_timestamp"),
        }
        last_row = {
            "tx_hash":  agg.get("last_tx_hash"),
            "sender":   agg.get("last_tx_sender"),
            "receiver": agg.get("last_tx_receiver"),
            "value":    agg.get("last_tx_value"),
            "timestamp":agg.get("last_tx_timestamp"),
        }

        return {
            "address": wallet_address,
            "symbol": "ETH",
            "balance": balance,
            "balance_usd": None,
            "total_received": total_received,
            "total_sent": total_sent,
            "transaction_count": int(agg.get("transaction_count") or 0),
            "unique_counterparties": int(agg.get("unique_counterparties") or 0),
            "first_tx": _row_to_tx_dict(first_row if first_row["tx_hash"] else None),
            "last_tx":  _row_to_tx_dict(last_row  if last_row["tx_hash"]  else None),
        }
    finally:
        cur.close()
        conn.close()

def get_wallet_risk_metrics(address: str, high_value_eth: float = 10.0, risk_score_cutoff: int = 70):
    """
    Menghitung:
      - % transaksi anomali (z-score |value_eth| >= 3)
      - % transaksi bernominal tinggi (>= high_value_eth)
      - % transaksi dengan counterparty berisiko tinggi (risk_score >= cutoff)
      - % transaksi dengan counterparty blacklisted (is_blacklisted = true)
    Catatan:
      - Tabel yang dipakai: transactions(sender, receiver, value_eth, tx_hash, block_time ...)
      - Mapping risiko: entity_risk(address, risk_score, is_blacklisted)
        (LEFT JOIN, jadi kalau tabel tak ada / kosong, hasilnya 0)
    """
    sql = """
    WITH tx AS (
        SELECT t.tx_hash,
               t.sender,
               t.receiver,
               t.value_eth::numeric AS value_eth
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
          CASE WHEN lower(t.sender)=lower(%(addr)s) THEN t.receiver ELSE t.sender END AS counterparty
        FROM tx t
    ),
    cp_risk AS (
        SELECT
          COUNT(*) FILTER (WHERE er.risk_score >= %(risk_cutoff)s)              AS risky_cnt,
          COUNT(*) FILTER (WHERE COALESCE(er.is_blacklisted, false) IS true)    AS blacklisted_cnt
        FROM counterparty c
        LEFT JOIN entity_risk er ON lower(er.address) = lower(c.counterparty)
    )
    SELECT
      (SELECT total_tx        FROM total)        AS total_tx,
      (SELECT anomaly_cnt     FROM anomaly)      AS anomaly_cnt,
      (SELECT high_value_cnt  FROM high_value)   AS high_value_cnt,
      (SELECT risky_cnt       FROM cp_risk)      AS risky_cnt,
      (SELECT blacklisted_cnt FROM cp_risk)      AS blacklisted_cnt
    ;
    """

    conn = get_db()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, {
            "addr": address,
            "high_value_eth": high_value_eth,
            "risk_cutoff": risk_score_cutoff,
        })
        row = cur.fetchone() or {}

    total = int(row.get("total_tx", 0) or 0)
    anomaly_cnt     = int(row.get("anomaly_cnt", 0) or 0)
    high_value_cnt  = int(row.get("high_value_cnt", 0) or 0)
    risky_cnt       = int(row.get("risky_cnt", 0) or 0)
    blacklisted_cnt = int(row.get("blacklisted_cnt", 0) or 0)

    def pct(x): 
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
            "scoreCutoff": int(risk_score_cutoff)
        },
        "blacklistedCounterparty": {
            "count": blacklisted_cnt,
            "percent": pct(blacklisted_cnt)
        }
    }
    
def get_wallet_risk_flags(address: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    addr_lower = address.lower()

    # Ambil risk profile (tanpa updated_at)
    cur.execute("""
        SELECT risk_score, risk_profile
        FROM wallet_risk
        WHERE LOWER(address) = %s
        LIMIT 1
    """, (addr_lower,))
    wr = cur.fetchone()

    # Ambil data blacklist
    cur.execute("""
        SELECT source, category, reason, added_on
        FROM blacklist_addresses
        WHERE LOWER(address) = %s
        ORDER BY added_on DESC NULLS LAST
    """, (addr_lower,))
    bl_rows = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "riskProfile": {
            "score": float(wr["risk_score"]) if wr and wr.get("risk_score") is not None else None,
            "profile": wr["risk_profile"] if wr and wr.get("risk_profile") else "Unknown"
        },
        "blacklist": {
            "isBlacklisted": bool(bl_rows),
            "entries": [
                {
                    "source": r["source"],
                    "category": r["category"],
                    "reason": r["reason"],
                    "added_on": r["added_on"].isoformat() if r.get("added_on") else None
                } for r in (bl_rows or [])
            ]
        }
    }