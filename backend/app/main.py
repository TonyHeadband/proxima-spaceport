import os
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from api.routes.api import router as api_router
from core.config import API_PREFIX, DEBUG, PROJECT_NAME, VERSION
from core.errors import DatabaseException
from database import Database
from dependencies import init_cryptography_key
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan_manager(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan manager to handle startup and shutdown events."""
    try:
        app.state.db = Database()
    except DatabaseException:
        raise RuntimeError("Failed to connect to the database")

    app.state.auth_key = init_cryptography_key(app)
    if not app.state.auth_key:
        raise RuntimeError("Failed to initialize encryption key")

    print(f"DEV mode:{os.getenv('DEV')}")

    yield

    app.state.db.engine.dispose()


app = FastAPI(
    title=PROJECT_NAME, version=VERSION, debug=DEBUG, lifespan=lifespan_manager
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=API_PREFIX)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, int]:
    return {"status": 200}
