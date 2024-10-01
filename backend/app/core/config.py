import os
from core.logger import setup_logger, log_step

logger = setup_logger('config')

class Settings:
    PROJECT_NAME: str = "Unified Vendor Catalog"
    SQLALCHEMY_DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///../../databases/sqlite/products.db")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()

log_step(logger, 1, f"Configuration loaded: PROJECT_NAME={settings.PROJECT_NAME}, DATABASE_URL={settings.SQLALCHEMY_DATABASE_URL}, LOG_LEVEL={settings.LOG_LEVEL}")