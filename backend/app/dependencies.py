from fastapi import Request
from sqlalchemy.orm import Session


def get_db(request: Request) -> Session:
    session: Session = request.app.state.db.get_session()
    try:
        yield session
    finally:
        session.close()
