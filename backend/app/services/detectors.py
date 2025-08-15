from .transaction_service import (
    detect_large_tx_for_wallet, 
    get_hourly_transaction_count,
    detect_recurring_transactions_raw,
    get_blacklist_interactions,
    get_risky_interactions,
    detect_repeated_value_transactions,
)
from .anomaly_service import log_anomaly

DETECTORS = {}

def register_detector(name):
    def deco(fn):
        DETECTORS[name] = fn
        return fn
    return deco

@register_detector('large_tx')
def detect_large_tx(wallet_address, conn):
    anomalies = detect_large_tx_for_wallet(wallet_address)
    results = []
    for s, r, v, ts in anomalies:
        reason = f"Transaksi besar: {v} ETH dari {s} ke {r} pada {ts}"
        log_anomaly(
            wallet_address=wallet_address,
            detector='heuristic:large_tx',
            reason=reason,
            metadata={"sender": s, "receiver": r, "value": float(v), "timestamp": ts.isoformat()}
        )
        results.append({
        'detector': 'large_tx',
        'reason': reason,
        'data': {'sender': s, 'receiver': r, 'value': v, 'timestamp': ts}
    })
    return results

@register_detector('hourly_tx_spike')
def detect_hourly_tx_spike(wallet_address, conn):
    sender_counts, receiver_counts = get_hourly_transaction_count(wallet_address)
    alerts = []

    for hour_bucket, count in sender_counts:
        reason = f"Spike transaksi kirim: {count} tx pada {hour_bucket}"
        log_anomaly(
            wallet_address=wallet_address,
            detector='heuristic:hourly_tx_spike',
            reason=reason,
            metadata={"direction": "sent", "hour_bucket": hour_bucket.isoformat(), "count": count}
        )
        alerts.append({
            'detector': 'hourly_tx_spike',
            'reason': reason,
            'data': {'direction': 'sent', 'hour_bucket': hour_bucket.isoformat(), 'count': count}
        })

    for hour_bucket, count in receiver_counts:
        reason = f"Spike transaksi terima: {count} tx pada {hour_bucket}"
        log_anomaly(
            wallet_address=wallet_address,
            detector='heuristic:hourly_tx_spike',
            reason=reason,
            metadata={"direction": "received", "hour_bucket": hour_bucket.isoformat(), "count": count}
        )
        alerts.append({
            'detector': 'hourly_tx_spike',
            'reason': reason,
            'data': {'direction': 'received', 'hour_bucket': hour_bucket.isoformat(), 'count': count}
        })

    return alerts

@register_detector('recurring_tx')
def detect_recurring_tx(wallet_address, conn):
    pattern = detect_recurring_transactions_raw(wallet_address)
    if not pattern:
        return []
    reason = f"Pola transaksi terdeteksi: {pattern}"
    log_anomaly(
        wallet_address=wallet_address,
        detector='heuristic:recurring_tx',
        reason=reason,
        metadata={"pattern": pattern}
    )
    return [{
        'detector': 'recurring_tx',
        'reason': reason,
        'data': {'pattern': pattern, 'wallet': wallet_address}
    }]

@register_detector('blacklist_interaction')
def detect_blacklist_interaction(wallet_address, conn):
    interactions = get_blacklist_interactions(wallet_address)
    results = []
    for tx in interactions:
        reason = f"Interaksi dengan address blacklist: {tx['blacklisted_party']} pada {tx['timestamp']}"
        log_anomaly(
            wallet_address=wallet_address,
            detector='heuristic:blacklist_interaction',
            reason=reason,
            metadata=tx
        )
        results.append({
            'detector': 'blacklist_interaction',
            'reason': reason,
            'data': tx
        })
    return results

@register_detector('risky_interaction')
def detect_risky_interaction(wallet_address, conn):
    interactions = get_risky_interactions(wallet_address)
    results = []
    for tx in interactions:
        reason = f"Interaksi dengan address risiko tinggi: {tx['risk_source']} pada {tx['timestamp']}"
        log_anomaly(
            wallet_address=wallet_address,
            detector='heuristic:risky_interaction',
            reason=reason,
            metadata=tx
        )
        results.append({
        'detector': 'risky_interaction',
        'reason': reason,
        'data': tx
    })
    return results

@register_detector('repeated_value_tx')
def detect_repeated_value(wallet_address, conn):
    grouped = detect_repeated_value_transactions(wallet_address)
    results = []
    for (sender, receiver, value), txs in grouped.items():
        reason = f"Transaksi berulang dengan nilai sama ({value} ETH) ke {receiver} dari {sender}"
        log_anomaly(
            wallet_address=wallet_address,
            detector='heuristic:repeated_value_tx',
            reason=reason,
            metadata={
                "sender": sender,
                "receiver": receiver,
                "value": float(value),
                "count": len(txs),
                "samples": txs[:5]  # hanya simpan sebagian
            }
        )
        results.append({
            'detector': 'repeated_value_tx',
            'reason': reason,
            'data': {
                "sender": sender,
                "receiver": receiver,
                "value": float(value),
                "count": len(txs)
            }
        })
    return results

def run_all_detectors(wallet_address, conn=None):
    results = {}
    for name, fn in DETECTORS.items():
        results[name] = fn(wallet_address, conn)
    return results
