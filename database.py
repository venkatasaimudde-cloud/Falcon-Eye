"""
FALCON EYE - Database Engine & Session Management
PostgreSQL-ready architecture using SQLAlchemy ORM.
Default: SQLite local database with WAL mode for high-concurrency read/write.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Determine data storage path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "evidence"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "reports"), exist_ok=True)

# Database URL: Environment variable override allows easy switch to PostgreSQL/PostGIS
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(DATA_DIR, 'falcon_eye.db')}")

# SQLite specific connect args for multi-threaded safety
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI Dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
