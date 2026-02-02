# app/db.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Loads DATABASE_URL from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Validate DATABASE_URL exists
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please create a .env file with DATABASE_URL=postgresql://..."
    )

# Engine = the connection "bridge" to PostgreSQL
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal = creates DB sessions when needed
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = parent class for all our table models
Base = declarative_base()

# Dependency function: gives a DB session to each request, then closes it
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
