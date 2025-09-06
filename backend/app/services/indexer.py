from fastapi import HTTPException, status
from datetime import datetime, timezone
from database import Repos, Credentials
import bcrypt

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.indexer import Repository, RepoCredentials


def create_new_repo(url: str, name: str, credentials_name: str,  db: Session) -> bool:
    # Logic to clone the repo and index its contents
    # For now, we'll just simulate success

    new_repo = Repos(url=url, name=name, indexed_at=datetime.now(
        timezone.utc), updated_at=datetime.now(timezone.utc), credentials_name=credentials_name)

    try:
        db.add(new_repo)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if "UNIQUE constraint failed" in str(e.orig):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Unique constraint violation!")
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Internal server error")
    except HTTPException:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="create_new_repo failed unexpectedly")

    return True


def list_repositories(db: Session) -> list[Repository]:
    return [Repository(**repo.as_dict()) for repo in db.query(Repos).all()]


def create_new_credentials(name: str, username: str, password: str, token: str, db: Session) -> bool:
    new_credentials = None
    hashed_password = None
    hashed_token = None

    if password:
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())

    if token:
        hashed_token = bcrypt.hashpw(
            token.encode('utf-8'), bcrypt.gensalt())

    new_credentials = Credentials(
        name=name, username=username, password=hashed_password, token=hashed_token)

    try:
        db.add(new_credentials)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if "UNIQUE constraint failed" in str(e.orig):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Unique constraint violation!")
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Internal server error")
    except HTTPException:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="create_new_credentials failed unexpectedly")

    print(f"Storing new credentials for: {name}")
    return True


def get_all_credentials(db: Session) -> list[RepoCredentials]:
    return [RepoCredentials(**cred.as_dict()) for cred in db.query(Credentials).all()]


def get_repo_info_by_name(name: str, db: Session) -> Repos | None:
    return db.query(Repos).filter(Repos.name == name).first()
