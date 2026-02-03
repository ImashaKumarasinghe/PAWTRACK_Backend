# app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class PetCreate(BaseModel):
    # Field(...)= required. Gives validation rules.
    title: str = Field(..., min_length=3, max_length=150)
    species: str = Field(..., pattern="^(DOG|CAT)$")  # only DOG/CAT allowed
    description: Optional[str] = Field(None, max_length=500)
    photo_url: Optional[str] = Field(None, max_length=500)  # Optional photo

    location_url: str = Field(..., max_length=500)
    location_text: Optional[str] = Field(None, max_length=150)

class PetOut(BaseModel):
    id: int
    title: str
    species: str
    description: Optional[str]
    photo_url: Optional[str]  # Optional photo
    location_url: str
    location_text: Optional[str]
    status: str
    created_at: datetime

    # Allows Pydantic to read SQLAlchemy objects
    class Config:
        from_attributes = True


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    phone_number: str = Field(..., min_length=7, max_length=20)
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)

class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone_number: str

    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"