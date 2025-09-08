from collections.abc import Iterator
from cryptography.fernet import Fernet
from datetime import datetime, timezone

from fastapi import HTTPException, status
from database import Repos, Credentials, Index

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.indexer import RepositoryModel, RepoCredentialsModel, NewIndexEntryModel

from utilities.github_utils import make_index_entry


def create_new_repo(url: str, branch: str, name: str, compose_folder: str, credentials_name: str,  db: Session) -> bool:
    new_repo = Repos(url=url, branch=branch, name=name, compose_folder=compose_folder, indexed_at=datetime.now(
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


def list_repositories(db: Session) -> list[RepositoryModel]:
    return [RepositoryModel(**repo.as_dict()) for repo in db.query(Repos).all()]


def get_repo_by_id(repo_id: str, db: Session) -> RepositoryModel | None:
    return db.query(Repos).filter(Repos.id == repo_id).first()


def create_new_credentials(name: str, username: str, password: str, token: str, db: Session, auth_key: bytes) -> bool:
    new_credentials = None
    encrypted_password = None
    encrypted_token = None

    if password:
        fernet = Fernet(auth_key)
        encrypted_password = fernet.encrypt(password.encode('utf-8'))

    if token:
        fernet = Fernet(auth_key)
        encrypted_token = fernet.encrypt(token.encode('utf-8'))

    new_credentials = Credentials(
        name=name, username=username, password=encrypted_password, token=encrypted_token)

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


def get_all_credentials(db: Session) -> list[RepoCredentialsModel]:
    return [RepoCredentialsModel(**cred.as_dict()) for cred in db.query(Credentials).all()]


def get_credentials_by_name(credentials_name: str, db: Session) -> RepoCredentialsModel | None:
    return db.query(Credentials).filter(Credentials.name == credentials_name).first()


def get_index_values(db: Session) -> list[dict[str, str | None]]:
    return [entry.as_dict() for entry in db.query(Index).all()]


def validate_uniqueness_index_entry(repo_id: int, db: Session) -> bool:
    existing_index = db.query(Index).filter(Index.repo_id == repo_id).first()
    return existing_index is None


def fetch_index_new_entries(db: Session, auth_key: bytes) -> Iterator[NewIndexEntryModel]:
    for entry in db.query(Repos).all():
        if not validate_uniqueness_index_entry(entry.id, db):
            continue

        cred = None
        if entry.credentials_name:
            cred = get_credentials_by_name(entry.credentials_name, db)
            if not cred:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Credentials for {entry.credentials_name} not found")

        new_entry = make_index_entry(RepositoryModel(
            **entry.as_dict()), credentials=cred, auth_key=auth_key)

        if new_entry:
            yield new_entry


async def rescan_index_values(force: bool, db: Session, auth_key: bytes):
    new_index_entries = fetch_index_new_entries(db, auth_key)
    for entry in new_index_entries:
        table_entry = Index(repo_id=entry.repo_id, compose_path=entry.compose_path,
                            indexed_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
        try:
            existing_index = db.query(Index).filter(
                Index.repo_id == table_entry.id).first()
            if existing_index:
                if force:
                    existing_index.compose_path = table_entry.compose_path
                    existing_index.updated_at = datetime.now(timezone.utc)
                    db.add(existing_index)
            else:
                db.add(table_entry)
        except HTTPException:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="rescan_index_values failed during the add of new entry")
    try:
        db.commit()
    except HTTPException:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="rescan_index_values failed during the commit of new entries")
