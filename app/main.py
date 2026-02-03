# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from .models import User
from .schemas import UserRegister, UserLogin, UserOut, TokenOut
from .auth_utils import hash_password, verify_password, create_access_token


from .db import Base, engine, get_db
from .models import Pet
from .schemas import PetCreate, PetOut

from .auth_dep import get_current_user_id


app = FastAPI(title="PawTrack API")

# Allow requests from your frontend (Next.js)
# For development: allow all localhost/127.0.0.1 variations
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",  # alternative ports
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     # who can access your API
    allow_credentials=True,    # allow cookies / auth headers later
    allow_methods=["*"],       # allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],       # allow all headers (Authorization etc.)
)


# ✅ Creates tables in PostgreSQL if they don't exist yet
Base.metadata.create_all(bind=engine)

@app.get("/")
def health_check():
    """
    Simple test route to confirm API is running.
    """
    return {"message": "PawTrack backend running ✅"}

@app.post("/pets", response_model=PetOut)
def create_pet(payload: PetCreate, db: Session = Depends(get_db)):
    """
    Create a new pet advertisement.
    Status defaults to AVAILABLE.
    """
    pet = Pet(**payload.model_dump())  # convert payload into model
    db.add(pet)                        # stage insert
    db.commit()                        # save to DB
    db.refresh(pet)                    # reload to get id, created_at
    return pet

@app.get("/pets", response_model=List[PetOut])
def list_available_pets(db: Session = Depends(get_db)):
    """
    List only AVAILABLE pets (so saved pets don't show on main list).
    """
    pets = db.query(Pet).filter(Pet.status == "AVAILABLE").order_by(Pet.created_at.desc()).all()
    return pets

@app.get("/pets/{pet_id}", response_model=PetOut)
def get_pet(pet_id: int, db: Session = Depends(get_db)):
    """
    View one pet advertisement including its map coordinates.
    """
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
    Only logged-in users can save pets.
    """
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    pet.status = "SAVED"
    db.commit()
    db.refresh(pet)
    return pet


#user part

@app.post("/auth/register", response_model=UserOut)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):

    # 1) confirm password check
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # 2) check email already exists
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    # 3) hash password
    hashed = hash_password(payload.password)

    # 4) create user row
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


#login route
@app.post("/auth/login", response_model=TokenOut)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # check password
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # create JWT token (store user id + email)
    token = create_access_token({"sub": str(user.id), "email": user.email})

    return {"access_token": token, "token_type": "bearer"}
