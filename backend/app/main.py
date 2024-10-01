from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routes import router
from core.config import settings
from core.logger import setup_logger, log_step, daily_log_maintenance
import os
import sqlite3
import asyncio

logger = setup_logger('main')

@asynccontextmanager
async def lifespan(app: FastAPI):
    log_step(logger, 1, "Starting up FastAPI application")
    
    # Log bakımı için bir background task başlat
    asyncio.create_task(periodic_log_maintenance())

    # Startup event
    db_path = '/databases/sqlite/products.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    log_step(logger, 2, "Initializing SQLite schema")
    with open('/databases/sqlite/init_schema.sql') as f:
        conn.executescript(f.read())

    log_step(logger, 3, "Checking if vendors table is empty")
    cursor.execute("SELECT COUNT(*) FROM vendors;")
    result = cursor.fetchone()
    vendor_count = result[0] if result else 0

    if vendor_count == 0:
        log_step(logger, 4, "Seeding vendors data")
        seed_file_path = '/databases/sqlite/seed_data.sql'
        if os.path.exists(seed_file_path):
            with open(seed_file_path) as f:
                conn.executescript(f.read())

    conn.close()

    log_step(logger, 5, "Startup complete")
    yield
    log_step(logger, 6, "Shutting down FastAPI application")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(router)

origins = ["*"]
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def periodic_log_maintenance():
    while True:
        daily_log_maintenance()
        await asyncio.sleep(24 * 60 * 60)  # 24 saat bekle

log_step(logger, 7, "FastAPI application configured and ready")