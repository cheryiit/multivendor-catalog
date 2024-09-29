from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routes import router
from core.database import get_db_connection
from core.config import settings
import os

# Define the lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    conn = get_db_connection()
    cursor = conn.cursor()

    # Initialize schema
    with open('/databases/sqlite/init_schema.sql') as f:
        conn.executescript(f.read())

    # Check if vendors table is empty
    cursor.execute("SELECT COUNT(*) FROM vendors;")
    vendor_count = cursor.fetchone()[0]

    if vendor_count == 0:
        # Seed the vendors data
        seed_file_path = '/databases/sqlite/seed_data.sql'
        if os.path.exists(seed_file_path):
            with open(seed_file_path) as f:
                conn.executescript(f.read())

    conn.close()

    # Yield control to run the app
    yield

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
