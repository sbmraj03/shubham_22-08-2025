from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.config import DATABASE_URL


# Create database engine using the connection URL
# same_thread=False allows SQLite to be used in multi-threaded apps
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

# Session factory to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables defined in models"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def get_db():
    """Provide a database session for queries"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Run table creation only if this file is executed directly
if __name__ == "__main__":
    create_tables()
