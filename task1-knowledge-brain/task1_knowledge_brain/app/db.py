import sqlite3
from contextlib import contextmanager
from config import DB_PATH

@contextmanager
def connect():
    con = sqlite3.connect(DB_PATH, timeout=30)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS articles (
          url TEXT PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL,
          content_hash TEXT NOT NULL, lastmod TEXT, active INTEGER NOT NULL DEFAULT 1,
          fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS chunks (
          id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT NOT NULL, title TEXT NOT NULL,
          heading TEXT, content TEXT NOT NULL, chunk_index INTEGER NOT NULL,
          UNIQUE(url, chunk_index)
        );
        CREATE TABLE IF NOT EXISTS ingestion (
          url TEXT PRIMARY KEY, status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
          error TEXT, updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS escalations (
          id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT NOT NULL, reason TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'open', expert_answer TEXT,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP, resolved_at TEXT
        );
        """)
