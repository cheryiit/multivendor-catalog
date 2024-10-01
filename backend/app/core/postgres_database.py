import os
import psycopg2
from psycopg2.extras import RealDictCursor
from core.logger import setup_logger, log_step

logger = setup_logger('postgres_database')

def get_postgres_connection():
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "product_catalog")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    
    log_step(logger, 1, f"Attempting to connect to PostgreSQL database: {POSTGRES_DB} on {POSTGRES_HOST}:{POSTGRES_PORT}")
    
    try:
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            cursor_factory=RealDictCursor
        )
        log_step(logger, 2, "Successfully connected to PostgreSQL database")
        return conn
    except psycopg2.Error as e:
        log_step(logger, 3, f"Failed to connect to PostgreSQL database. Error: {str(e)}")
        raise

def close_postgres_connection(conn):
    if conn:
        log_step(logger, 4, "Closing PostgreSQL database connection")
        conn.close()
        log_step(logger, 5, "PostgreSQL database connection closed")