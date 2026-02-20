import re
from datetime import datetime
from typing import Any, List, Optional
from bson import ObjectId
from pymongo import ReturnDocument
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.db import get_db
from app.deps import require_admin
from app.models import BookIn, BookOut, BookUpdate

router = APIRouter()


def _serialize_book(doc: dict[str, Any]) -> BookOut:
    return BookOut(
        id=str(doc["_id"]),
        title=doc["title"],
        author=doc["author"],
        description=doc.get("description"),
        genre=doc.get("genre"),
        published_year=doc.get("published_year"),
        isbn=doc.get("isbn"),
        created_at=doc["created_at"],
        read_count=doc.get("read_count", 0),
    )


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_book(payload: BookIn, db=Depends(get_db)):
    doc = payload.model_dump()
    doc.update({"created_at": datetime.utcnow(), "read_count": 0})
    result = await db.books.insert_one(doc)
    created = await db.books.find_one({"_id": result.inserted_id})
    return _serialize_book(created)


@router.get("", response_model=List[BookOut])
async def list_books(
    db=Depends(get_db),
    title: Optional[str] = Query(default=None),
    author: Optional[str] = Query(default=None),
    genre: Optional[str] = Query(default=None),
    year_min: Optional[int] = Query(default=None),
    year_max: Optional[int] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    sort_dir: str = Query(default="desc"),
):
    filters: dict[str, Any] = {}
    if title:
        filters["title"] = {"$regex": re.escape(title), "$options": "i"}
    if author:
        filters["author"] = {"$regex": re.escape(author), "$options": "i"}
    if genre:
        filters["genre"] = {"$regex": re.escape(genre), "$options": "i"}
    if year_min is not None or year_max is not None:
        year_filter: dict[str, Any] = {}
        if year_min is not None:
            year_filter["$gte"] = year_min
        if year_max is not None:
            year_filter["$lte"] = year_max
        filters["published_year"] = year_filter

    sort_field = "created_at" if sort_by not in {"created_at", "read_count", "title"} else sort_by
    sort_direction = -1 if sort_dir.lower() == "desc" else 1

    cursor = db.books.find(filters).sort(sort_field, sort_direction).skip(skip).limit(limit)
    items = [ _serialize_book(doc) async for doc in cursor ]
    return items


@router.get("/{book_id}", response_model=BookOut)
async def get_book(book_id: str, db=Depends(get_db)):
    if not ObjectId.is_valid(book_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid book id")
    doc = await db.books.find_one_and_update(
        {"_id": ObjectId(book_id)},
        {"$inc": {"read_count": 1}},
        return_document=ReturnDocument.AFTER,
    )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return _serialize_book(doc)


@router.put("/{book_id}", response_model=BookOut, dependencies=[Depends(require_admin)])
async def update_book(book_id: str, payload: BookUpdate, db=Depends(get_db)):
    if not ObjectId.is_valid(book_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid book id")
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No updates provided")
    doc = await db.books.find_one_and_update(
        {"_id": ObjectId(book_id)},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return _serialize_book(doc)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_book(book_id: str, db=Depends(get_db)):
    if not ObjectId.is_valid(book_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid book id")
    result = await db.books.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return None
