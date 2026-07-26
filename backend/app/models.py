import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core.commands import Command, DeviceType
from .database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class Floor(Base):
    __tablename__ = "floors"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    plan_image_path: Mapped[str | None] = mapped_column(String, nullable=True)

    rooms: Mapped[list["Room"]] = relationship(back_populates="floor", cascade="all, delete-orphan")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    floor_id: Mapped[str] = mapped_column(ForeignKey("floors.id"))
    name: Mapped[str] = mapped_column(String)
    # Liste de {"xPct": float, "yPct": float} formant le polygone cliquable, en % de l'image de fond.
    zone_shape: Mapped[list] = mapped_column(JSON, default=list)

    floor: Mapped["Floor"] = relationship(back_populates="rooms")
    devices: Mapped[list["Device"]] = relationship(back_populates="room")


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String)
    device_type: Mapped[DeviceType] = mapped_column(SAEnum(DeviceType, native_enum=False))
    room_id: Mapped[str | None] = mapped_column(ForeignKey("rooms.id"), nullable=True)
    adapter_name: Mapped[str] = mapped_column(String)
    external_id: Mapped[str] = mapped_column(String)
    supported_commands: Mapped[list] = mapped_column(JSON, default=list)
    last_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    room: Mapped["Room | None"] = relationship(back_populates="devices")


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    days_of_week: Mapped[list] = mapped_column(JSON, default=list)
    time: Mapped[str] = mapped_column(String)  # "HH:MM"

    actions: Mapped[list["ScenarioAction"]] = relationship(
        back_populates="scenario", cascade="all, delete-orphan", order_by="ScenarioAction.order"
    )


class ScenarioAction(Base):
    __tablename__ = "scenario_actions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("scenarios.id"))
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"))
    command: Mapped[Command] = mapped_column(SAEnum(Command, native_enum=False))
    params: Mapped[dict] = mapped_column(JSON, default=dict)
    order: Mapped[int] = mapped_column(Integer, default=0)

    scenario: Mapped["Scenario"] = relationship(back_populates="actions")
