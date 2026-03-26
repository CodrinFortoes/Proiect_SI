import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from models import Base

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "crypto_manager.db")
DB_URL = f"sqlite:///{DEFAULT_DB_PATH}"

engine = create_engine(
    DB_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    Base.metadata.create_all(bind=engine)
    print(f"[DB] Baza de date initializata: {DEFAULT_DB_PATH}")


def drop_db():
    Base.metadata.drop_all(bind=engine)
    print("[DB] Toate tabelele au fost sterse.")


def get_session() -> Session:
    return SessionLocal()


if __name__ == "__main__":
    init_db()
    print("[DB] Tabelele au fost create cu succes!")