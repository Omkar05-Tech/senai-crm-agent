from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Yield wrapper for explicit session cleanup on every single endpoint hit
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()