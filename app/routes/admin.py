from datetime import datetime, timedelta
from typing import Any, List
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.db import get_db
from app.deps import require_admin
from app.routes.books import _serialize_book

router = APIRouter()


def _serialize_read(doc: dict[str, Any]) -> dict[str, Any]:
    return {"id": str(doc["_id"]), "title": doc["title"], "read_count": doc.get("read_count", 0)}


@router.get("/insights/reads")
async def reads_insights(
    db=Depends(get_db),
    limit: int = Query(default=5, ge=1, le=20),
):
    pipeline = [{"$group": {"_id": None, "total": {"$sum": "$read_count"}}}]
    total_reads = 0
    async for row in db.books.aggregate(pipeline):
        total_reads = row.get("total", 0)

    most_read = [
        _serialize_read(doc) async for doc in db.books.find({}).sort("read_count", -1).limit(limit)
    ]
    least_read = [
        _serialize_read(doc) async for doc in db.books.find({}).sort("read_count", 1).limit(limit)
    ]
    reads_per_book = [
        _serialize_read(doc) async for doc in db.books.find({}).sort("title", 1)
    ]

    return {
        "total_reads": total_reads,
        "most_read": most_read,
        "least_read": least_read,
        "reads_per_book": reads_per_book,
    }


@router.get("/insights/recent")
async def recent_books(
    db=Depends(get_db),
    limit: int = Query(default=10, ge=1, le=50),
):
    docs = [
        _serialize_book(doc) async for doc in db.books.find({}).sort("created_at", -1).limit(limit)
    ]
    return {"recent": docs}
