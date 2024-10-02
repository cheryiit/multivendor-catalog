import sqlite3
from typing import Generator
from core.logger import setup_logger, log_step

logger = setup_logger('database')

# backend/app/core/database.py

def get_db_connection() -> Generator:
    db_path = '/databases/sqlite/products.db'
    log_step(logger, 1, f"Attempting to connect to database: {db_path}")
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        log_step(logger, 2, "Database connection established successfully")
        try:
            yield conn
        finally:
            log_step(logger, 3, "Closing database connection")
            conn.close()
            log_step(logger, 4, "Database connection closed")
    except sqlite3.Error as e:
        log_step(logger, 5, f"Error connecting to database: {str(e)}")
        raise
