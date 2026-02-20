import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB = os.getenv("MONGODB_DB", "bookhub")


def init_db(app: FastAPI) -> None:
    if not MONGODB_URL:
        raise RuntimeError("MONGODB_URL is not set")
    client = AsyncIOMotorClient(MONGODB_URL)
    app.state.mongo_client = client
    app.state.db = client[MONGODB_DB]


def close_db(app: FastAPI) -> None:
    client = app.state.mongo_client
    client.close()


def get_db(request: Request):
    return request.app.state.db
