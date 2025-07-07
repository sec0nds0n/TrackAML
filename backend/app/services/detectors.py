from .transaction_service import (
    detect_large_tx_for_wallet, 
    get_hourly_transaction_count,
    detect_recurring_transactions_raw,
)
DETECTORS = {}

def register_detector(name):
    def deco(fn):
        DETECTORS[name] = fn
        return fn
    return deco

@register_detector('large_tx')
def detect_large_tx(wallet_address, conn):
    # gunakan detect_large_tx_for_wallet yang sudah ada
    anomalies = detect_large_tx_for_wallet(wallet_address)
    return [{'detector': 'large_tx', 'data': {'sender': s, 'receiver': r, 'value': v, 'timestamp': ts}} 
            for s,r,v,ts in anomalies]
    
@register_detector('hourly_tx_spike')
def detect_hourly_tx_spike(wallet_address, conn):
    """
    Deteksi jika dalam satu jam wallet mengirim atau menerima
    >50 transaksi—menghasilkan alert per bucket jam.
    """
    sender_counts, receiver_counts = get_hourly_transaction_count(wallet_address)

    alerts = []
    # Spike untuk transaksi kirim
    for hour_bucket, count in sender_counts:
        alerts.append({
            'detector': 'hourly_tx_spike',
            'data': {
                'direction': 'sent',
                'hour_bucket': hour_bucket.isoformat(),
                'count': count
            }
        })

    # Spike untuk transaksi terima
    for hour_bucket, count in receiver_counts:
        alerts.append({
            'detector': 'hourly_tx_spike',
            'data': {
                'direction': 'received',
                'hour_bucket': hour_bucket.isoformat(),
                'count': count
            }
        })

    return alerts

@register_detector('recurring_tx')
def detect_recurring_tx(wallet_address, conn):
    """
    Deteksi pola transaksi rutin (harian, mingguan, bulanan).
    """
    pattern = detect_recurring_transactions_raw(wallet_address)
    if not pattern:
        return []
    return [{
        'detector': 'recurring_tx',
        'data': {
            'pattern': pattern,
            'wallet': wallet_address
        }
    }]