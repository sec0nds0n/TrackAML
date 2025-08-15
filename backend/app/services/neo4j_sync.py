import psycopg2
from neo4j import GraphDatabase
from decimal import Decimal
from datetime import datetime
from ..database import get_db_connection

# Konfigurasi koneksi Neo4j
neo4j_conn = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

BATCH_SIZE = 1000  # Sesuaikan dengan kapasitas sistem
def is_neo4j_running():
    """Cek apakah Neo4j dalam keadaan menyala."""
    try:
        with neo4j_conn.session() as session:
            result = session.run("RETURN 1")
            return result.single()[0] == 1  
    except Exception as e:
        print(f"❌ Neo4j Error: {e}")
        return False
    
def migrate_transactions():
    """Migrasi data transaksi dari PostgreSQL ke Neo4j."""
    pg_conn = get_db_connection()
    pg_cursor = pg_conn.cursor()
    
    pg_cursor.execute("SELECT sender, receiver, value, timestamp FROM transactions")
    transactions = pg_cursor.fetchall()
    
    with neo4j_conn.session() as session:
        tx = session.begin_transaction()
        for i, (sender, receiver, value, timestamp) in enumerate(transactions):
            value = float(value) if isinstance(value, Decimal) else value
            timestamp = timestamp.isoformat() if isinstance(timestamp, datetime) else str(timestamp)

            tx.run("""
                MERGE (s:Wallet {address: $sender})
                MERGE (r:Wallet {address: $receiver})
                MERGE (s)-[:SEND {value: $value, timestamp: $timestamp}]->(r)
            """, sender=sender, receiver=receiver, value=value, timestamp=timestamp)

            if i % BATCH_SIZE == 0:
                tx.commit()
                tx = session.begin_transaction()

        tx.commit()


    
    pg_cursor.close()
    pg_conn.close()
    
    return len(transactions)

def label_blacklisted_wallets():
    """Memberi label is_blacklisted ke wallet dari database PostgreSQL."""
    pg_conn = get_db_connection()
    pg_cursor = pg_conn.cursor()
    
    pg_cursor.execute("SELECT address FROM blacklist_addresses")
    blacklisted_wallets = [row[0] for row in pg_cursor.fetchall()]
    
    pg_cursor.close()
    pg_conn.close()

    if not blacklisted_wallets:
        print("Tidak ada wallet blacklist ditemukan.")
        return 0

    with neo4j_conn.session() as session:
        batch_size = 500
        for i in range(0, len(blacklisted_wallets), batch_size):
            batch = blacklisted_wallets[i:i+batch_size]
            session.run("""
                UNWIND $addresses AS addr
                MATCH (w:Wallet {address: addr})
                SET w.is_blacklisted = true
            """, addresses=batch)

    print(f"✅ Label is_blacklisted berhasil diterapkan ke {len(blacklisted_wallets)} wallet.")
    return len(blacklisted_wallets)