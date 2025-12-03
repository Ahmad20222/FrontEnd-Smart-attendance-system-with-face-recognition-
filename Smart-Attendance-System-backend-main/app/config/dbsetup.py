"""
Database configuration and session management.

This module creates the SQLModel engine and exposes a `SessionDep`
FastAPI dependency that yields a database `Session` for each request.
"""

import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import event
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL)

@event.listens_for(engine, "connect")
def enable_sqlite_fk(dbapi_connection, connection_record):
    """
    Ensure SQLite foreign key constraints are enforced.

    This hook is called for each new DBAPI connection.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.close()


def get_session():
    """
    Dependency generator that yields a database `Session`.

    The session is automatically closed when the request is finished.
    """
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]