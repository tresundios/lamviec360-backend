import os
import time
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_NAME = os.getenv("POSTGRES_DB", "lamviec360")
DATABASE_USER = os.getenv("POSTGRES_USER", "admin")
DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DATABASE_HOST = os.getenv("POSTGRES_HOST", "postgres")
DATABASE_PORT = os.getenv("POSTGRES_PORT", "5432")

print(f"[DB] Connecting to {DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}")

DATABASE_URL = (
    f"postgresql://{quote_plus(DATABASE_USER)}:{quote_plus(DATABASE_PASSWORD)}"
    f"@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db(max_retries: int = 30, wait_seconds: int = 2):
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"[DB] Connected successfully on attempt {attempt}")
            return
        except Exception as e:
            print(f"[DB] Attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(wait_seconds)
    raise RuntimeError("Could not connect to database after multiple retries")
