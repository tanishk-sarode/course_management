# Dependency: config.py
# Delivers:
# SQLAlchemy engine
# SessionLocal
# get_db dependency

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def get_db():
    """
    Dependency that provides a database session.
    Handles connection and disconnection.
    """
    db: Session = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Database connection error: {e}")
    finally:
        db.close()

    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
