from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..deps import get_current_user
from ..schemas import CamelModel, RoomOut, ZonePoint

router = APIRouter(prefix="/api/rooms", tags=["rooms"], dependencies=[Depends(get_current_user)])


class RoomCreate(CamelModel):
    floor_id: str
    name: str
    zone_shape: list[ZonePoint] = []


class RoomUpdate(CamelModel):
    name: str | None = None
    zone_shape: list[ZonePoint] | None = None


@router.post("", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(payload: RoomCreate, db: Session = Depends(get_db)):
    floor = db.get(models.Floor, payload.floor_id)
    if floor is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Étage introuvable")
    room = models.Room(
        floor_id=payload.floor_id,
        name=payload.name,
        zone_shape=[p.model_dump(by_alias=True) for p in payload.zone_shape],
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.patch("/{room_id}", response_model=RoomOut)
def update_room(room_id: str, payload: RoomUpdate, db: Session = Depends(get_db)):
    room = db.get(models.Room, room_id)
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pièce introuvable")
    data = payload.model_dump(exclude_unset=True, by_alias=False)
    if "zone_shape" in data and data["zone_shape"] is not None:
        room.zone_shape = [p.model_dump(by_alias=True) for p in payload.zone_shape]
        data.pop("zone_shape")
    for field, value in data.items():
        setattr(room, field, value)
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: str, db: Session = Depends(get_db)):
    room = db.get(models.Room, room_id)
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pièce introuvable")
    db.delete(room)
    db.commit()
