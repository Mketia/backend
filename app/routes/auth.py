import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from app.auth import create_access_token, get_password_hash, verify_password
from app.db import get_db
from app.models import TokenResponse, UserCreate, UserPublic

logger = logging.getLogger("uvicorn.error")

router = APIRouter()




def _serialize_user(doc: dict) -> UserPublic:
    return UserPublic(id=str(doc["_id"]), email=doc["email"], role=doc["role"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db=Depends(get_db)):
    try:
        existing = await db.users.find_one({"email": payload.email.lower()})
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        user_doc = {
            "email": payload.email.lower(),
            "hashed_password": get_password_hash(payload.password),
            "role": payload.role,  # Use the role from the payload
        }
        result = await db.users.insert_one(user_doc)
        created = await db.users.find_one({"_id": result.inserted_id})
        return _serialize_user(created)
    except Exception as e:
        logger.error(f"Error in register API: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserCreate, db=Depends(get_db)):
    user = await db.users.find_one({"email": payload.email.lower()})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(user["_id"]), "role": user["role"]})
    return TokenResponse(access_token=token)
