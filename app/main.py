# app/main.py
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

from .models import User, Pet
from .schemas import (
    UserRegister, UserLogin, UserOut, TokenOut,
    PetCreate, PetOut
)
from .auth_utils import hash_password, verify_password, create_access_token
from .db import Base, engine, get_db
from .auth_dep import get_current_user_id
from .bot_knowledge import FAQ


app = FastAPI(title="PawTrack API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.get("/")
def health_check():
    return {"message": "PawTrack backend running ✅"}


@app.post("/pets", response_model=PetOut)
def create_pet(payload: PetCreate, db: Session = Depends(get_db)):
    # ✅ safer than model_dump for beginners
    pet = Pet(**payload.dict())
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


# ✅ UPDATED: supports status filter
@app.get("/pets", response_model=List[PetOut])
def list_pets(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(default="AVAILABLE")  # AVAILABLE by default
):
    """
    GET /pets -> returns pets filtered by status
    - /pets                 -> AVAILABLE
    - /pets?status=ADOPTED  -> ADOPTED
    """
    status_upper = (status or "AVAILABLE").upper()
    pets = (
        db.query(Pet)
        .filter(Pet.status == status_upper)
        .order_by(Pet.created_at.desc())
        .all()
    )
    return pets


@app.get("/pets/{pet_id}", response_model=PetOut)
def get_pet(pet_id: int, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet


@app.post("/pets/{pet_id}/save", response_model=PetOut)
def save_pet(
    pet_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Only logged-in users can adopt/save pets.
    """
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    pet.status = "ADOPTED"
    pet.adopted_at = datetime.utcnow()
    db.commit()
    db.refresh(pet)

    return pet


# ---------------- USER AUTH ----------------

@app.post("/auth/register", response_model=UserOut)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = hash_password(payload.password)

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        phone_number=payload.phone_number,
        password_hash=hashed
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=TokenOut)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/chat")
def chat_bot(payload: dict, db: Session = Depends(get_db)):
    """
    Free rule-based chatbot endpoint.
    Expects: { "message": "text..." }
    Returns: { "reply": "text..." }
    """
    message = (payload.get("message") or "").lower().strip()

    if not message:
        return {"reply": "Please type a message 😊"}

    # ✅ DB-powered answers (live info)
    if "available" in message and ("pets" in message or "pet" in message):
        count = db.query(Pet).filter(Pet.status == "AVAILABLE").count()
        return {"reply": f"Right now, there are {count} pets available on PawTrack 🐾"}

    if "adopted" in message:
        count = db.query(Pet).filter(Pet.status == "ADOPTED").count()
        return {"reply": f"So far, {count} pets have been adopted 🎉"}

    # ✅ Rule-based FAQ answers
    for item in FAQ:
        for tag in item["tags"]:
            if tag in message:
                return {"reply": item["answer"]}

    # ✅ fallback
    return {
        "reply": "I can help with: registration, login, adoption, reporting pets, and map location. Try asking: 'How to adopt?'"
    }

