from fastapi import FastAPI
from app.db import init_db, close_db
from app.routes.auth import router as auth_router
from app.routes.books import router as books_router
from app.routes.admin import router as admin_router

app = FastAPI(title="BookHub API")


@app.on_event("startup")
async def startup_event() -> None:
    init_db(app)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    close_db(app)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(books_router, prefix="/books", tags=["books"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
