from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from .config import Config

engine: Engine = create_engine(
    Config.DATABASE_URL,          # if you used the safer Config.database_url()
    pool_pre_ping=True,
    connect_args={"sslmode": Config.DB_SSLMODE},
)

def run_sql(sql: str, params: dict | None = None):
    with engine.connect() as conn:
        return conn.execute(text(sql), params or {}).mappings().all()

def scalar_sql(sql: str, params: dict | None = None):
    with engine.connect() as conn:
        return conn.execute(text(sql), params or {}).scalar()