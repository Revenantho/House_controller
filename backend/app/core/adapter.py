from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from .commands import Command, DeviceType


@dataclass
class DeviceState:
    is_open: bool | None
    position: int | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiscoveredDevice:
    external_id: str
    name: str
    device_type: DeviceType
    supported_commands: list[Command]
    state: DeviceState


class Adapter(ABC):
    """Contrat unique qu'un protocole (Somfy/Overkiz, Zigbee, MQTT...) doit implémenter
    pour se brancher sur le hub. Rien en dehors de adapters/<nom>/ ne doit connaître
    le vocabulaire d'un protocole précis."""

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def discover_devices(self) -> list[DiscoveredDevice]: ...

    @abstractmethod
    async def send_command(self, external_id: str, command: Command, **params: Any) -> DeviceState: ...

    @abstractmethod
    async def get_state(self, external_id: str) -> DeviceState: ...
