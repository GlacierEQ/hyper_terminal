# db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "hyper_terminal.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
      CREATE TABLE IF NOT EXISTS items (
        id        TEXT   PRIMARY KEY,
        source    TEXT,
        title     TEXT,
        url       TEXT,
        published TEXT,
        content   TEXT
      )
    """)
    conn.commit()
    return conn

def insert_item(conn, item):
    """
    item: dict with keys id, source, title, url, published, content
    """
    c = conn.cursor()
    c.execute("""
      INSERT OR IGNORE INTO items (id, source, title, url, published, content)
      VALUES (:id, :source, :title, :url, :published, :content)
    """, item)
    conn.commit()

