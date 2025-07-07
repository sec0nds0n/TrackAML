from ..database import get_db_connection
from decimal import Decimal
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

import requests, time, socks, socket
from bs4 import BeautifulSoup

def get_wallet_summary(wallet_address):
    
    conn = get_db_connection()
    cur = conn.cursor()

    # Total ETH yang diterima oleh wallet
    cur.execute("""
        SELECT COALESCE(SUM(value), 0) FROM transactions 
        WHERE receiver = %s
    """, (wallet_address,))
    total_received = cur.fetchone()[0]

    # Total ETH yang dikirim oleh wallet
    cur.execute("""
        SELECT COALESCE(SUM(value), 0) FROM transactions 
        WHERE sender = %s
    """, (wallet_address,))
    total_sent = cur.fetchone()[0]

    # Saldo = Total diterima - Total dikirim
    balance = total_received - total_sent

    # Transaksi pertama berdasarkan timestamp
    cur.execute("""
        SELECT sender, receiver, value, timestamp FROM transactions 
        WHERE sender = %s OR receiver = %s
        ORDER BY timestamp ASC LIMIT 1
    """, (wallet_address, wallet_address))
    first_transaction = cur.fetchone()

    # Transaksi terakhir berdasarkan timestamp
    cur.execute("""
        SELECT sender, receiver, value, timestamp FROM transactions 
        WHERE sender = %s OR receiver = %s
        ORDER BY timestamp DESC LIMIT 1
    """, (wallet_address, wallet_address))
    last_transaction = cur.fetchone()

    cur.close()
    conn.close()

    return {
        "balance": balance,
        "total_received": total_received,
        "total_sent": total_sent,
        "first_transaction": first_transaction,
        "last_transaction": last_transaction
    }

def get_top_transactions(wallet_address):
    """Mengambil 3 transaksi terbesar dari/ke wallet."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT tx_hash, sender, receiver, value, timestamp 
        FROM transactions 
        WHERE sender = %s OR receiver = %s
        ORDER BY value DESC 
        LIMIT 3
    """, (wallet_address, wallet_address))
    transactions = cur.fetchall()
    cur.close()
    conn.close()
    return transactions

def get_top_receivers(wallet_address):
    """Mengambil 3 alamat yang paling sering menerima transaksi dari wallet."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT receiver, COUNT(*) as count 
        FROM transactions 
        WHERE sender = %s
        GROUP BY receiver 
        ORDER BY count DESC 
        LIMIT 3
    """, (wallet_address,))
    receivers = cur.fetchall()
    cur.close()
    conn.close()
    return receivers

def get_top_senders(wallet_address):
    """Mengambil 3 alamat yang paling sering mengirim transaksi ke wallet."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT sender, COUNT(*) as count 
        FROM transactions 
        WHERE receiver = %s
        GROUP BY sender 
        ORDER BY count DESC 
        LIMIT 3
    """, (wallet_address,))
    senders = cur.fetchall()
    cur.close()
    conn.close()
    return senders

def check_wallet_in_history(wallet_address):
    """Cek apakah wallet sudah ada di wallet_history."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT 1 FROM wallet_history WHERE address = %s", (wallet_address,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result is not None

def is_wallet_blacklisted(wallet_address):
    """Cek apakah wallet masuk dalam daftar blacklist."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT source, reason FROM blacklist_addresses WHERE address = %s", (wallet_address,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    if result:
        return {"source": result[0], "reason": result[1]}
    return None

