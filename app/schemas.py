# app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PetCreate(BaseModel):
    # Field(...)= required. Gives validation rules.
    title: str = Field(..., min_length=3, max_length=150)
    species: str = Field(..., pattern="^(DOG|CAT)$")  # only DOG/CAT allowed
    description: Optional[str] = Field(None, max_length=500)

    location_url: str = Field(..., max_length=500)
    location_text: Optional[str] = Field(None, max_length=150)

class PetOut(BaseModel):
    id: int
    title: str
    species: str
    description: Optional[str]
    location_url: str
    location_text: Optional[str]
    status: str
    created_at: datetime

    # Allows Pydantic to read SQLAlchemy objects
    class Config:
        from_attributes = True
