from pathlib import Path


def create_temp_db_file(tmp_path: Path):
    db_file = tmp_path / "test_database.db"
    db_path = f"sqlite:///{db_file.as_posix()}"
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base

    engine = create_engine(db_path, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    class TempDB:
        def __init__(self, engine, session_local):
            self.engine = engine
            self.session = session_local

        def get_session(self):
            return self.session()

    return TempDB(engine, SessionLocal)


def remove_temp_db_file(tmp_db):
    try:
        tmp_db.engine.dispose()
    except Exception:
        pass
