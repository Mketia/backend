from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str
    password: str


class UserPublic(BaseModel):
    id: str
    email: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class BookIn(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    genre: Optional[str] = None
    published_year: Optional[int] = None
    isbn: Optional[str] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    published_year: Optional[int] = None
    isbn: Optional[str] = None


class BookOut(BaseModel):
    id: str
    title: str
    author: str
    description: Optional[str] = None
    genre: Optional[str] = None
    published_year: Optional[int] = None
    isbn: Optional[str] = None
    created_at: datetime
    read_count: int = Field(default=0)
