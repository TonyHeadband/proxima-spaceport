from api.routes.api import router as api_router
from core.config import API_PREFIX, DEBUG, PROJECT_NAME, VERSION
from fastapi import FastAPI, status

from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware

from database import Database

from core.errors import DatabaseException


@asynccontextmanager
async def lifespan_manager(app: FastAPI):
    """Lifespan manager to handle startup and shutdown events."""
    try:
        app.state.db = Database()
    except DatabaseException:
        raise RuntimeError("Failed to connect to the database")

    yield

    # write here post shutdown code


app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    debug=DEBUG,
    lifespan=lifespan_manager
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=API_PREFIX)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": 200}
