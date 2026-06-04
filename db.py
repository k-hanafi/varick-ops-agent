import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "ops.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
