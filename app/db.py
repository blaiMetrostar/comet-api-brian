from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# SqlAlchemy Setup
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
# Use in-memory SQLite database for testing
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:  # For other databases, use the default connection settings
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_recycle=300
    )


def get_db():
    """Provide a database session for dependency injection.

    Creates a database session, yields it for use in the request,
    and ensures it is properly closed after the request completes.

    Yields:
        Session: SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# SqlAlchemy Setup
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
