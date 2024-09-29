# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routes import router
from core.config import settings
import os
import sqlite3
import logging

# Define the lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up...")

    # Startup event
    db_path = '/databases/sqlite/products.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Initialize schema
    with open('/databases/sqlite/init_schema.sql') as f:
        conn.executescript(f.read())

    # Check if vendors table is empty
    cursor.execute("SELECT COUNT(*) FROM vendors;")
    result = cursor.fetchone()
    vendor_count = result[0] if result else 0

    if vendor_count == 0:
        # Seed the vendors data
        seed_file_path = '/databases/sqlite/seed_data.sql'
        if os.path.exists(seed_file_path):
            with open(seed_file_path) as f:
                conn.executescript(f.read())

    conn.close()

    # Yield control to run the app
    logging.info("Startup complete.")
    yield
    logging.info("Shutting down...")

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
