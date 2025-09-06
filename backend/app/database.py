from sqlalchemy import create_engine, UniqueConstraint, String, DateTime, LargeBinary
from sqlalchemy.orm import sessionmaker, declarative_base, mapped_column

from uuid import uuid4

DATABASE_URL = "sqlite:///./database.db"

Base = declarative_base()


class Database:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL, connect_args={
                                    "check_same_thread": False})
        self.session = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine)

        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self.session()


class BaseTable(Base):
    __abstract__ = True

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Repos(BaseTable):
    __tablename__ = "repos"

    id = mapped_column(String, primary_key=True, index=True,
                       default=lambda: str(uuid4()))
    url = mapped_column(String, index=True)
    name = mapped_column(String, index=True)
    credentials_name = mapped_column(String)
    indexed_at = mapped_column(DateTime)  # ISO formatted datetime string
    updated_at = mapped_column(DateTime)  # ISO formatted datetime string

    __table_args__ = (UniqueConstraint(
        'url', 'name', name='_id_url_name_uc'),)

    def as_dict(self) -> dict[str, str | None]:
        return {
            "id": self.id,
            "url": self.url,
            "name": self.name,
            "credentials_name": self.credentials_name,
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
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
