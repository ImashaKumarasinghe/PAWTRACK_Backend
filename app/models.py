# app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .db import Base

class Pet(Base):
    """
    This class becomes a PostgreSQL table called 'pets'.
    Each attribute = a column in the table.
    """
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)  # auto id

    title = Column(String(150), nullable=False)         # short title
    species = Column(String(10), nullable=False)        # "DOG" or "CAT"
    description = Column(String(500), nullable=True)    # optional
    photo_url = Column(String(500), nullable=True)      # photo link (optional)

    location_url = Column(String(500), nullable=False)   # Google Maps link
    location_text = Column(String(150), nullable=True)   # Optional: "Near bus stop"

    status = Column(String(10), default="AVAILABLE")    # AVAILABLE / SAVED
    created_at = Column(DateTime, default=datetime.utcnow)  # auto time
