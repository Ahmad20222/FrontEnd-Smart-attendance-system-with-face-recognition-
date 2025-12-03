"""
Status CRUD Operations

This module provides database operations for Status entities including:
- Retrieving status ID by status type
- Creating new status records
"""

from sqlmodel import Session, select

from app.models.status import Status


def get_status_id(status: str, session: Session) -> int | None:
    """
    Retrieve a status ID by status type string.
    
    Args:
        status: Status type string (e.g., "Present", "Absent")
        session: Database session
        
    Returns:
        Status ID (primary key), or None if not found
    """
    statement = select(Status).where(Status.status_type == status)
    status_obj = session.exec(statement).first()
    if not status_obj:
        return None
    return status_obj.status_id


def add_new_status(status: str, session: Session) -> Status | None:
    """
    Create a new status record in the database.
    
    Args:
        status: Status type string (e.g., "Present", "Absent")
        session: Database session
        
    Returns:
        Created Status object, or None if creation fails
    """
    try:
        new_status = Status(status_type=status)
        session.add(new_status)
        session.commit()
        session.refresh(new_status)
        return new_status
    except Exception:
        session.rollback()
        return None