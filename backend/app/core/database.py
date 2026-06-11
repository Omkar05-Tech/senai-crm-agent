from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Add pool_pre_ping=True to handle Supabase disconnecting idle connections
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # <-- THIS IS THE MAGIC FIX
    pool_recycle=1800    # Recycle connections every 30 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()