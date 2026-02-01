# app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PetCreate(BaseModel):
    # Field(...)= required. Gives validation rules.
    title: str = Field(..., min_length=3, max_length=150)
    species: str = Field(..., pattern="^(DOG|CAT)$")  # only DOG/CAT allowed
    description: Optional[str] = Field(None, max_length=500)

    latitude: float
    longitude: float

class PetOut(BaseModel):
    id: int
    title: str
    species: str
    description: Optional[str]
    latitude: float
    longitude: float
    status: str
    created_at: datetime

    # Allows Pydantic to read SQLAlchemy objects
    class Config:
        from_attributes = True
