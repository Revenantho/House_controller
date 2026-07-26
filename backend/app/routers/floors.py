from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..deps import get_current_user
from ..schemas import CamelModel, FloorOut, RoomOut

router = APIRouter(prefix="/api/floors", tags=["floors"], dependencies=[Depends(get_current_user)])


class FloorCreate(CamelModel):
    name: str
    display_order: int = 0
    plan_image_path: str | None = None


class FloorUpdate(CamelModel):
    name: str | None = None
    display_order: int | None = None
    plan_image_path: str | None = None


@router.get("", response_model=list[FloorOut])
def list_floors(db: Session = Depends(get_db)):
    return db.query(models.Floor).order_by(models.Floor.display_order).all()


@router.post("", response_model=FloorOut, status_code=status.HTTP_201_CREATED)
def create_floor(payload: FloorCreate, db: Session = Depends(get_db)):
    floor = models.Floor(**payload.model_dump())
    db.add(floor)
    db.commit()
    db.refresh(floor)
    return floor


@router.patch("/{floor_id}", response_model=FloorOut)
def update_floor(floor_id: str, payload: FloorUpdate, db: Session = Depends(get_db)):
    floor = db.get(models.Floor, floor_id)
    if floor is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Étage introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(floor, field, value)
    db.commit()
    db.refresh(floor)
    return floor


@router.delete("/{floor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_floor(floor_id: str, db: Session = Depends(get_db)):
    floor = db.get(models.Floor, floor_id)
    if floor is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Étage introuvable")
    db.delete(floor)
    db.commit()


@router.get("/{floor_id}/rooms", response_model=list[RoomOut])
def list_rooms_for_floor(floor_id: str, db: Session = Depends(get_db)):
    floor = db.get(models.Floor, floor_id)
    if floor is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Étage introuvable")
    return floor.rooms
