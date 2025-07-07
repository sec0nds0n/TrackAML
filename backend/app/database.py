import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
def get_db_connection():
    """Membuat koneksi ke database PostgreSQL."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )