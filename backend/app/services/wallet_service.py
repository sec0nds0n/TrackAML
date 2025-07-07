from ..database import get_db_connection
from ..services.risk_analysis import calculate_wallet_risk, fetch_transactions_from_db
from ..services.neo4j_sync import is_neo4j_running, migrate_transactions, label_blacklisted_wallets
from ..services.kyc_service import is_wallet_blacklisted, get_top_transactions, get_top_receivers, get_top_senders

import requests
import pandas as pd
import numpy as np
import joblib
import os
import psycopg2
import psycopg2.extras

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
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