"""
Person CRUD Operations

This module provides database operations for Person entities including:
- Creating new person records
- Retrieving persons by ID or embedding ID
"""

from sqlmodel import Session, select
from app.models.person import Person, PersonCreate, PersonPublic


def create_person(
    person_data: PersonCreate, 
    session: Session
) -> PersonPublic | None:
    """
    Create a new person record in the database.
    
    Args:
        person_data: Person creation data (first_name, last_name, embedding_id, etc.)
        session: Database session
        
    Returns:
        Created person as PersonPublic object, or None if creation fails
    """
    try:
        db_person = Person.model_validate(person_data)
        session.add(db_person)
        session.commit()
        session.refresh(db_person)
        return PersonPublic.model_validate(db_person)
    except Exception as e:
        session.rollback()
        return None


def get_person_by_pk(
    id: int, 
    session: Session
) -> PersonPublic | None:
    """
    Retrieve a person by their primary key (person_id).
    
    Args:
        id: Person ID (primary key)
        session: Database session
        
    Returns:
        Person as PersonPublic object, or None if not found
    """
    person = session.get(Person, id)
    if not person:
        return None
    return PersonPublic.model_validate(person)


def get_person_by_embedding_id(
    embedding_id: int, 
    session: Session
) -> PersonPublic | None:
    """
    Retrieve a person by their associated embedding ID.
    
    Args:
        embedding_id: Embedding ID (foreign key)
        session: Database session
        
    Returns:
        Person as PersonPublic object, or None if not found
    """
    statement = select(Person).where(Person.embedding_id == embedding_id)
    person = session.exec(statement).first()
    if not person:
        return None
    return PersonPublic.model_validate(person)