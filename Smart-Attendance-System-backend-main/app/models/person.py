from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel



class PersonBase(SQLModel):
    first_name: str
    last_name: str
    

class Person(PersonBase, table=True, sqlite_autoincrement=True):
    person_id: int | None = Field(default=None, primary_key=True)
    embedding_id: int = Field(foreign_key="embedding.embedding_id", unique=True, index=True)

    embeddings: Optional["Embedding"] = Relationship(back_populates="Person")
    attendances: List["Attendance"] = Relationship(back_populates="Person")


class PersonPublic(PersonBase):
    person_id: int

class PersonCreate(PersonBase):
    embedding_id: int
