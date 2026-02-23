import os

class Config:
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set")

    DB_SSLMODE = os.environ.get("DB_SSLMODE", "require")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")