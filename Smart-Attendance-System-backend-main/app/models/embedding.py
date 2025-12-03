from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
from app.models.person import Person

class Embedding(SQLModel, table=True, sqlite_autoincrement=True):
    embedding_id: int | None = Field(default=None, primary_key=True)
    vector: bytes  # encrypted facial embedding

    Person: Optional["Person"] = Relationship(back_populates="embeddings")