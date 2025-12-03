"""
Authentication helpers.

This module is responsible for:
- Creating JWT access tokens for administrators.
- Validating tokens and loading the current administrator from the DB.
"""

from datetime import datetime, timedelta, timezone
import os
from typing import Annotated, Optional

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config.dbsetup import SessionDep
from app.cruds.admin_crud import get_admin_by_email
from app.models.administrator import AdministratorPublic


SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")

auth_dep = Annotated[str, Depends(oauth2_scheme)]


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a signed JWT access token.

    Args:
        data: Payload to encode (will be copied and extended with `exp`).
        expires_delta: Optional explicit expiry interval. If not provided,
            a default of 15 minutes is used.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_admin(token: auth_dep, session: SessionDep) -> Optional[AdministratorPublic]:
    """
    Resolve the current administrator from a Bearer token.

    This is used as a FastAPI dependency on protected endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    current_admin = get_admin_by_email(email, session)
    if current_admin is None:
        raise credentials_exception
    return current_admin