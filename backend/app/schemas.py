from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from .core.commands import Command, DeviceType


class CamelModel(BaseModel):
    """Les champs Python restent en snake_case, le JSON exposé au frontend React est en
    camelCase (miroir exact des interfaces TypeScript dans frontend/src/types)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


# --- Auth ---


class LoginRequest(CamelModel):
    username: str
    password: str


class UserOut(CamelModel):
    id: str
    username: str


# --- Floors / Rooms ---


class ZonePoint(CamelModel):
    x_pct: float
    y_pct: float


class FloorOut(CamelModel):
    id: str
    name: str
    display_order: int
    plan_image_path: str | None = None


class RoomOut(CamelModel):
    id: str
    floor_id: str
    name: str
    zone_shape: list[ZonePoint]


# --- Devices ---


class DeviceStateOut(CamelModel):
    is_open: bool | None
    position: int | None
    raw: dict = {}


class DeviceOut(CamelModel):
    id: str
    name: str
    device_type: DeviceType
    room_id: str | None
    adapter_name: str
    supported_commands: list[Command]
    last_state: DeviceStateOut | None
    last_synced_at: datetime | None


class CommandRequest(CamelModel):
    command: Command
    params: dict = {}


# --- Scenarios ---


class ScenarioActionOut(CamelModel):
    id: str
    device_id: str
    command: Command
    params: dict
    order: int


class ScenarioOut(CamelModel):
    id: str
    name: str
    enabled: bool
    days_of_week: list[int]
    time: str
    actions: list[ScenarioActionOut]
