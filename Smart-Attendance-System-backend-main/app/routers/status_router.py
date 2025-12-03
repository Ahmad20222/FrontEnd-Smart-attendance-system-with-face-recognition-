"""
Status router.

Provides endpoints for managing attendance status types (e.g. Present,
Absent, Late).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.config.dbsetup import SessionDep
from app.cruds.status_crud import add_new_status, get_status_id
from app.models.administrator import Administrator
from app.models.status import Status
from app.services.auth import get_current_admin

status_router = APIRouter(prefix="/status", tags=["Status"])


current_admin_dep = Annotated[Administrator, Depends(get_current_admin)]

@status_router.post("/", response_model=Status)
def add_status(
    status_name: str,
    session: SessionDep,
    current_user: current_admin_dep,
) -> Status:
    """
    Create a new status type.

    The `status_name` is a simple string (e.g. "Present").
    Only authenticated administrators may call this endpoint.
    """
    new_status = add_new_status(status_name, session)
    if not new_status:
        raise HTTPException(status_code=400, detail="status creation failed")
    return new_status

