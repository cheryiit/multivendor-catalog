# backend/app/core/database.py

import sqlite3
from typing import Generator

def get_db_connection() -> Generator:
    db_path = '/databases/sqlite/products.db'
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
