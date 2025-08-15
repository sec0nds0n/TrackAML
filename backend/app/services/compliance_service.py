from ..database import get_db_connection
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List, Optional

import datetime, json

def get_wallet_compliance_score():
    """
    Hitung persentase wallet normal (bukan high-risk & bukan blacklist).
    Asumsi kolom alamat di kedua tabel bernama 'address'. 
    Jika di wallet_risk kolomnya 'wallet_address', ganti di query UNION di bawah.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Total unik wallet yang kita ketahui (gabungan wallet_risk & blacklist)
    cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT DISTINCT address FROM wallet_risk
            UNION
            SELECT DISTINCT address FROM blacklist_addresses
        ) AS u
    """)
    total_wallets = cur.fetchone()[0] or 0

    # High risk (dari wallet_risk)
    cur.execute("""
        SELECT COUNT(DISTINCT address)
        FROM wallet_risk
        WHERE LOWER(TRIM(risk_profile)) = 'high risk'
    """)
    high_risk_wallets = cur.fetchone()[0] or 0

    # Blacklisted
    cur.execute("SELECT COUNT(DISTINCT address) FROM blacklist_addresses")
    blacklisted_wallets = cur.fetchone()[0] or 0

    # Anomalous = union high risk + blacklist (hindari double count)
    cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT DISTINCT address
            FROM wallet_risk
            WHERE LOWER(TRIM(risk_profile)) = 'high risk'
            UNION
            SELECT DISTINCT address FROM blacklist_addresses
        ) AS a
    """)
    anomalous_wallets = cur.fetchone()[0] or 0

    cur.close(); conn.close()

    if total_wallets == 0:
        score = 100.0
    else:
        normal_wallets = total_wallets - anomalous_wallets
        score = round(100.0 * normal_wallets / total_wallets, 2)

    return {
        "score": score,
        "total_wallets": int(total_wallets),
        "anomalous_wallets": int(anomalous_wallets),
        "high_risk_wallets": int(high_risk_wallets),
        "blacklisted_wallets": int(blacklisted_wallets),
    }
    
def compute_compliance_scores(*, 
    has_kyc_profile: bool,
    sanctions_hits: int,
    risky_interactions: int,
    recurring_flags: int,
    high_freq_flags: int
) -> Dict[str, int]:
    kyc = 85 if has_kyc_profile else 55
    txmon = max(0, 90 - (high_freq_flags * 12 + recurring_flags * 10))
    sanctions = max(0, 90 - sanctions_hits * 30)
    riskasm = max(0, 90 - risky_interactions * 15)
    regulatory = round((kyc + txmon + sanctions + riskasm) / 4)
    return {
        "kyc_compliance": kyc,
        "transaction_monitoring": txmon,
        "sanctions_screening": sanctions,
        "risk_assessment": riskasm,
        "regulatory_compliance": regulatory
    }

def overall_score(scores: Dict[str, int]) -> int:
    keys = ["kyc_compliance","transaction_monitoring","sanctions_screening","risk_assessment","regulatory_compliance"]
    return round(sum(scores[k] for k in keys) / len(keys))