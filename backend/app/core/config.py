import os

class Settings:
    PROJECT_NAME: str = "Unified Vendor Catalog"
    SQLALCHEMY_DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///../../databases/sqlite/products.db")

settings = Settings()
