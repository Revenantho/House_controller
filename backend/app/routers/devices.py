from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models
from ..core.adapter import DeviceState
from ..core.commands import Command, DeviceType
from ..core.registry import AdapterRegistry, DeviceBusyError, UnknownAdapterError
from ..database import get_db
from ..deps import get_current_user, get_registry
from ..schemas import CamelModel, CommandRequest, DeviceOut
from .ws import manager

router = APIRouter(prefix="/api/devices", tags=["devices"], dependencies=[Depends(get_current_user)])


class DeviceUpdate(CamelModel):
    name: str | None = None
    room_id: str | None = None


def _apply_state(device: models.Device, state: DeviceState) -> None:
    device.last_state = {"isOpen": state.is_open, "position": state.position, "raw": state.raw}
    device.last_synced_at = datetime.now(timezone.utc)


@router.get("", response_model=list[DeviceOut])
def list_devices(
    room_id: str | None = None,
    type: DeviceType | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Device)
    if room_id:
        query = query.filter(models.Device.room_id == room_id)
    if type:
        query = query.filter(models.Device.device_type == type)
    return query.all()


@router.get("/{device_id}", response_model=DeviceOut)
def get_device(device_id: str, db: Session = Depends(get_db)):
    device = db.get(models.Device, device_id)
    if device is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Équipement introuvable")
    return device


@router.patch("/{device_id}", response_model=DeviceOut)
def update_device(device_id: str, payload: DeviceUpdate, db: Session = Depends(get_db)):
    device = db.get(models.Device, device_id)
    if device is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Équipement introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(device, field, value)
    db.commit()
    db.refresh(device)
    return device


@router.post("/{device_id}/command", response_model=DeviceOut)
async def send_command(
    device_id: str,
    payload: CommandRequest,
    db: Session = Depends(get_db),
    registry: AdapterRegistry = Depends(get_registry),
):
    device = db.get(models.Device, device_id)
    if device is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Équipement introuvable")
    if payload.command not in device.supported_commands:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Commande {payload.command} non supportée par cet équipement",
        )
    try:
        state = await registry.send_command(
            device.adapter_name, device.external_id, payload.command, **payload.params
        )
    except DeviceBusyError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except UnknownAdapterError as exc:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)) from exc

    _apply_state(device, state)
    db.commit()
    db.refresh(device)

    device_out = DeviceOut.model_validate(device)
    await manager.broadcast(device_out.model_dump(by_alias=True, mode="json"))
    return device_out


@router.post("/discover", response_model=list[DeviceOut])
async def discover_devices(
    db: Session = Depends(get_db),
    registry: AdapterRegistry = Depends(get_registry),
):
    """Relance la découverte de l'adaptateur et met à jour l'état en cache des équipements
    déjà connus (association par adapter_name + external_id) — n'invente pas de nouveaux
    équipements en base, cf. tâche différée sur la configuration de la maison."""
    updated: list[models.Device] = []
    known_devices = db.query(models.Device).all()
    adapters_used = {d.adapter_name for d in known_devices}
    for adapter_name in adapters_used:
        discovered = {d.external_id: d for d in await registry.discover_devices(adapter_name)}
        for device in known_devices:
            if device.adapter_name != adapter_name:
                continue
            found = discovered.get(device.external_id)
            if found is not None:
                _apply_state(device, found.state)
                updated.append(device)
    db.commit()
    for device in updated:
        db.refresh(device)
    return updated
