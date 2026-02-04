# app/models.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .db import Base


class Pet(Base):
    """
    PostgreSQL table: pets
    """
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(150), nullable=False)
    species = Column(String(10), nullable=False)  # DOG / CAT
    description = Column(String(500), nullable=True)
    photo_url = Column(String(500), nullable=True)

    location_url = Column(String(500), nullable=False)
    location_text = Column(String(150), nullable=True)

    status = Column(String(10), default="AVAILABLE")  # AVAILABLE / ADOPTED
    created_at = Column(DateTime, default=datetime.utcnow)
    adopted_at = Column(DateTime, nullable=True)  # ✅ moved INSIDE Pet


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), nullable=False)

    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
