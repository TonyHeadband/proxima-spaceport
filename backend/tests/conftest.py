from typing import Any
from tests.db_helpers import create_temp_db_file
import importlib
from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import init_cryptography_key
from pathlib import Path


def _make_temp_database(tmp_path: Path) -> Any:
    return create_temp_db_file(tmp_path)


@pytest.fixture
def tmp_db(tmp_path: Path) -> Any:
    return _make_temp_database(tmp_path)


@pytest.fixture
def client(tmp_db: Any) -> Generator[TestClient, None, None]:
    # Attach the temp DB and initialize auth_key.
    # Prevent the application's lifespan manager from running (it would create the real Database)
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def _no_lifespan(app_for_lifespan):
        yield

    # override the router lifespan to avoid production startup logic
    app.router.lifespan_context = _no_lifespan

    app.state.db = tmp_db
    # create encryption key entry in the test DB
    app.state.auth_key = init_cryptography_key(app)

    # monkeypatch GitHub helper to prevent network calls
    for util_mod in ("app.utilities.github_utils", "utilities.github_utils"):
        try:
            m = importlib.import_module(util_mod)
            setattr(m, "make_index_entry", lambda repo,
                    credentials, auth_key: None)
        except Exception:
            pass
    for svc_mod in ("app.services.indexer", "services.indexer"):
        try:
            m = importlib.import_module(svc_mod)
            setattr(m, "make_index_entry", lambda repo,
                    credentials, auth_key: None)
        except Exception:
            pass

    with TestClient(app) as client:
        yield client


@pytest.fixture
def api_v1() -> str:
    from app.core.config import API_PREFIX
    return API_PREFIX + "/v1"
