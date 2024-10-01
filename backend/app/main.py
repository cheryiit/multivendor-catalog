from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routes import router
from core.config import settings
from core.logger import setup_logger, log_step
import os
import sqlite3

logger = setup_logger('main')

@asynccontextmanager
async def lifespan(app: FastAPI):
    log_step(logger, 1, "Starting up FastAPI application")

    # Startup event
    db_path = '/databases/sqlite/products.db'
    log_step(logger, 2, f"Connecting to SQLite database: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Initialize schema
    log_step(logger, 3, "Initializing SQLite schema")
    with open('/databases/sqlite/init_schema.sql') as f:
        conn.executescript(f.read())

    # Check if vendors table is empty
    log_step(logger, 4, "Checking if vendors table is empty")
    cursor.execute("SELECT COUNT(*) FROM vendors;")
    result = cursor.fetchone()
    vendor_count = result[0] if result else 0

    if vendor_count == 0:
        # Seed the vendors data
        log_step(logger, 5, "Seeding vendors data")
        seed_file_path = '/databases/sqlite/seed_data.sql'
        if os.path.exists(seed_file_path):
            with open(seed_file_path) as f:
                conn.executescript(f.read())
        log_step(logger, 6, "Vendors data seeded successfully")
    else:
        log_step(logger, 6, f"Vendors table already contains {vendor_count} records")

    conn.close()
    log_step(logger, 7, "SQLite database connection closed")

    # Yield control to run the app
    log_step(logger, 8, "Startup complete. Yielding control to FastAPI")
    yield
    log_step(logger, 9, "Shutting down FastAPI application")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

log_step(logger, 10, "Including API router")
app.include_router(router)

origins = ["*"]
    
log_step(logger, 11, "Adding CORS middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

log_step(logger, 12, "FastAPI application setup complete")