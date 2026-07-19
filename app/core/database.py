import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

logger = logging.getLogger(__name__)

# Declare globals, but don't initialize them yet
engine = None
SessionLocal = None


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def setup_database():
    """Initialize the database engine and create tables."""
    global engine, SessionLocal

    logger.info(f"Connecting to database: {settings.DATABASE_URL}")

    # allow multiple threads
    connect_args = {}
    if "sqlite" in settings.DATABASE_URL:
        connect_args = {"check_same_thread": False}

    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        echo=settings.DEBUG
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables (In production, you would use Alembic migrations instead of this)
    logger.info("Creating database tables if they do not exist...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database setup complete.")



def get_db():
    """
    Dependency generator for FastAPI routes.
    Yields a database session and ensures it is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
