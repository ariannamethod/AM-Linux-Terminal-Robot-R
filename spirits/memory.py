import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).with_name("memory.db")


def _init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS events (ts REAL, role TEXT, content TEXT)")
    conn.commit()
    conn.close()


def log(role: str, content: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO events VALUES (?, ?, ?)", (time.time(), role, content))
    conn.commit()
    conn.close()


def last_user_command() -> str:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT content FROM events WHERE role='user' ORDER BY ts DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else ""


_init_db()
