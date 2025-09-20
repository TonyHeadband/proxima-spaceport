from sqlalchemy import create_engine, UniqueConstraint, String, DateTime, LargeBinary, ForeignKey
from sqlalchemy.orm import sessionmaker, mapped_column, DeclarativeBase
from sqlalchemy.orm import Session

from uuid import uuid4
from typing import Any

DATABASE_URL = "sqlite:///./database.db"


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self) -> None:
        self.engine = create_engine(DATABASE_URL, connect_args={
                                    "check_same_thread": False})
        self.session = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine)

        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        return self.session()


class BaseTable(Base):
    __abstract__ = True

    def as_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Repos(BaseTable):
    __tablename__ = "repos"

    id = mapped_column(String, primary_key=True, index=True,
                       default=lambda: str(uuid4()))
    url = mapped_column(String, index=True)
    name = mapped_column(String, index=True)
    branch = mapped_column(String, default="main")
    compose_folder = mapped_column(String, nullable=True)
    credentials_name = mapped_column(String)
    indexed_at = mapped_column(DateTime)  # ISO formatted datetime string
    updated_at = mapped_column(DateTime)  # ISO formatted datetime string

    __table_args__ = (UniqueConstraint(
        'name', 'url', 'branch', name='_id_name_url_branch_uc'),)

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "url": self.url,
            "branch": self.branch,
            "name": self.name,
            "compose_folder": self.compose_folder,
            "credentials_name": self.credentials_name,
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else "",
            "updated_at": self.updated_at.isoformat() if self.updated_at else "",
        }


class Credentials(BaseTable):
    __tablename__ = "credentials"

    id = mapped_column(String, primary_key=True, index=True,
                       default=lambda: str(uuid4()))
    name = mapped_column(String, index=True)
    username = mapped_column(String)
    password = mapped_column(LargeBinary, nullable=True)
    token = mapped_column(LargeBinary, nullable=True)

    __table_args__ = (UniqueConstraint(
        'name', 'username', name='_id_name_username_uc'),)


class Index(BaseTable):
    __tablename__ = "index"

    id = mapped_column(String, primary_key=True, index=True,
                       default=lambda: str(uuid4()))
    repo_id = mapped_column(String, ForeignKey("repos.id"), index=True)
    compose_path = mapped_column(String)
    indexed_at = mapped_column(DateTime)  # ISO formatted datetime string
    updated_at = mapped_column(DateTime)  # ISO formatted datetime string

    def as_dict(self) -> dict[str, str | None]:
        return {
            "id": self.id,
            "repo_id": self.repo_id,
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Auth(BaseTable):
    __tablename__ = "auth"

    key = mapped_column(LargeBinary, primary_key=True)
