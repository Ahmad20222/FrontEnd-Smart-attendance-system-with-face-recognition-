"""
Attendance CRUD Operations

This module provides database operations for Attendance entities including:
- Retrieving all attendance records
- Retrieving attendance by ID
- Creating new attendance records
"""

from typing import Optional
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.models.attendance import Attendance, AttendanceCreate, AttendanceDTO
from app.models.person import Person
from app.models.status import Status


def get_attendances(session: Session) -> list[AttendanceDTO] | None:
    """
    Retrieve all attendance records with person and status information.
    
    Args:
        session: Database session
        
    Returns:
        List of AttendanceDTO objects, or None if no records found
    """
    statement = (
        select(Attendance)
        .options(selectinload(Attendance.Person), selectinload(Attendance.status))
    )

    attendances = session.exec(statement).all()

    if not attendances:
        return []

    return [
        AttendanceDTO(
            attendance_id=a.attendance_id,
            date=a.datum,
            first_name=a.Person.first_name,
            last_name=a.Person.last_name,
            status_type=a.status.status_type
        )
        for a in attendances
    ]


def get_attendance_by_pk(id: int, session: Session) -> Optional[AttendanceDTO]:
    """
    Retrieve a specific attendance record by its primary key.
    
    Args:
        id: Attendance ID (primary key)
        session: Database session
        
    Returns:
        AttendanceDTO object, or None if not found
    """
    statement = (
        select(Attendance)
        .where(Attendance.attendance_id == id)
        .options(
            selectinload(Attendance.Person),
            selectinload(Attendance.status)
        )
    )
    result = session.exec(statement).first()
    if not result:
        return None

    return AttendanceDTO(
        attendance_id=result.attendance_id,
        date=result.datum,
        first_name=result.Person.first_name,
        last_name=result.Person.last_name,
        status_type=result.status.status_type
    )


def add_attendance(
    attendance: AttendanceCreate, 
    session: Session
) -> Optional[AttendanceDTO]:
    try:
        # Check if person_id exists
        from app.cruds.person_crud import get_person_by_pk
        person = get_person_by_pk(attendance.person_id, session)
        if not person:
            raise ValueError(f"Person with id {attendance.person_id} does not exist")

        # Check if status_id exists
        from app.cruds.status_crud import get_status_id
        status = session.get(Status, attendance.status_id)
        if not status:
            raise ValueError(f"Status with id {attendance.status_id} does not exist")

        db_attendance = Attendance.model_validate(attendance)
        session.add(db_attendance)
        session.commit()
        session.refresh(db_attendance)

        return get_attendance_by_pk(db_attendance.attendance_id, session)

    except Exception as e:
        session.rollback()
        print("Error adding attendance:", e)
        return None


