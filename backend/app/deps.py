from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .registry_singleton import get_registry


def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Non authentifié")
    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Non authentifié")
    return user


__all__ = ["get_current_user", "get_registry"]
