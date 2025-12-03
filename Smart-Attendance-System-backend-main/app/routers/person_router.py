"""
Person router.

Exposes endpoints to:
- Create a new person.
- Retrieve an existing person by primary key.

All endpoints are protected so that only authenticated administrators
can call them.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.config.dbsetup import SessionDep
from app.cruds.person_crud import create_person, get_person_by_pk
from app.models.administrator import Administrator
from app.models.person import PersonCreate, PersonPublic
from app.services.auth import get_current_admin

current_admin_dep = Annotated[Administrator, Depends(get_current_admin)]

person_router = APIRouter(prefix="/person", tags=["Person"])


@person_router.post("/", response_model=PersonPublic)
def create_new_person(
    person: PersonCreate,
    session: SessionDep,
    current_user: current_admin_dep,
) -> PersonPublic:
    """
    Create a new person record.

    The `current_user` dependency ensures that only authenticated
    administrators can create new persons.
    """
    result = create_person(person, session)
    if result is None:
        raise HTTPException(status_code=400, detail="Person creation failed")
    return result


@person_router.get("/", response_model=PersonPublic)
def get_person_by_id(
    id: int,
    session: SessionDep,
    current_user: current_admin_dep,
) -> PersonPublic:
    """
    Retrieve a person by primary key.

    Raises:
        HTTPException(404): If the person does not exist.
    """
    person = get_person_by_pk(id, session)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person
