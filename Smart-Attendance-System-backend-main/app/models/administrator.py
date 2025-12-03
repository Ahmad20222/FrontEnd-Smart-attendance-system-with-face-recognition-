from datetime import date, time, datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship




class AdministratorBase(SQLModel):
    first_name: str
    surname: str
    email: str


class Administrator(AdministratorBase, table=True, sqlite_autoincrement=True):
    admin_id: int | None = Field(default=None, primary_key=True)
    first_name: str
    surname: str
    password: str  # always hashed
    email: str = Field(index=True, unique=True)

class AdministratorPublic(AdministratorBase):
    admin_id: int


class AdministratorCreate(AdministratorBase):
    password: str


class TokenResponse(SQLModel):
    access_token: str
    token_type: str
    admin: AdministratorPublic
