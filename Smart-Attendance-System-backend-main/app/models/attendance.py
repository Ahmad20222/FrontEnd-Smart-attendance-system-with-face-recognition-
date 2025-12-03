from datetime import date, time, datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
from sqlalchemy.types import Date as SA_Date, Time as SA_Time



class AttendanceBase(SQLModel):
    datum: date = Field(default_factory=date.today, sa_type=SA_Date)

class Attendance(AttendanceBase, table=True, sqlite_autoincrement=True):
    attendance_id: int | None = Field(default=None, primary_key=True)
    person_id: int = Field(foreign_key="person.person_id")
    status_id: int = Field(foreign_key="status.status_id")

    Person: Optional["Person"] = Relationship(back_populates="attendances")
    status: Optional["Status"] = Relationship(back_populates="attendances")

class AttendanceDTO(SQLModel):
    attendance_id: int
    date: date
    first_name: str
    last_name: str
    status_type: str

class AttendanceCreate(AttendanceBase):
    person_id: int
    status_id: int