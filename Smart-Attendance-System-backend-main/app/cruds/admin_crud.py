"""
Administrator CRUD Operations

This module provides database operations for Administrator entities including:
- Retrieving administrators by email
- Verifying administrator credentials
- Creating new administrator accounts
"""

from typing import Optional
from sqlmodel import Session, select

from app.models.administrator import (
    Administrator,
    AdministratorCreate,
    AdministratorPublic,
)
from app.services.password_utils import verify_password


def get_admin_by_email(email: str, session: Session) -> Optional[Administrator]:
    """
    Retrieve an administrator by their email address.
    
    Args:
        email: Administrator email address
        session: Database session
        
    Returns:
        Administrator object, or None if not found
    """
    statement = select(Administrator).where(Administrator.email == email)
    result = session.exec(statement).first()
    if not result:
        return None
    return Administrator.model_validate(result)


def verify_admin(
    email: str, 
    entered_password: str, 
    session: Session
) -> Optional[AdministratorPublic]:
    """
    Verify administrator credentials (email and password).
    
    Args:
        email: Administrator email address
        entered_password: Plain text password to verify
        session: Database session
        
    Returns:
        AdministratorPublic object if credentials are valid, None if admin not found
        
    Raises:
        ValueError: If password is incorrect
    """
    admin = get_admin_by_email(email, session)
    if not admin:
        return None

    stored_hash = admin.password
    if verify_password(entered_password, stored_hash):
        return AdministratorPublic.model_validate(admin)
    else:
        raise ValueError("Password is not correct")


def create_new_admin(
    admin: AdministratorCreate, 
    session: Session
) -> Optional[AdministratorPublic]:
    """
    Create a new administrator account in the database.
    
    Note: Password should already be hashed before calling this function.
    
    Args:
        admin: Administrator creation data (email, password)
        session: Database session
        
    Returns:
        Created administrator as AdministratorPublic object, or None if creation fails
    """
    try:
        new_admin = Administrator(**admin.model_dump())
        session.add(new_admin)
        session.commit()
        session.refresh(new_admin)
        return AdministratorPublic.model_validate(new_admin)
    except Exception:
        session.rollback()
        return None