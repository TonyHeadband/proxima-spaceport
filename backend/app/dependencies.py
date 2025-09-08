from collections.abc import Generator

from cryptography.fernet import Fernet
from database import Auth
from fastapi import FastAPI, Request
from sqlalchemy.orm import Session


def get_db(request: Request) -> Generator[Session, None, None]:
    session: Session = request.app.state.db.get_session()
    try:
        yield session
    finally:
        session.close()


def get_cryptography_key(request: Request) -> bytes | None:
    if hasattr(request.app.state, "auth_key"):
        return request.app.state.auth_key
    return None


def init_cryptography_key(app: FastAPI) -> bytes | None:
    session = app.state.db.get_session()
    try:
        key = session.query(Auth).first()
        if not key:
            new_key = Auth(key=Fernet.generate_key())
            session.add(new_key)
            session.commit()
            return new_key.key
        return key.key
    except Exception:
        session.rollback()
        raise Exception("Failed to create encryption key in database")
    finally:
        session.close()
