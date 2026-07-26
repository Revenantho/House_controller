import asyncio
from collections import defaultdict

from .adapter import Adapter, DeviceState, DiscoveredDevice
from .commands import Command

LOCK_TIMEOUT_SECONDS = 5.0


class DeviceBusyError(Exception):
    """Levée quand une commande ou un rafraîchissement est déjà en cours pour cet équipement."""


class UnknownAdapterError(Exception):
    pass


class AdapterRegistry:
    """Point d'entrée unique entre l'API et les adaptateurs de protocole.
    Sérialise les accès concurrents à un même équipement physique via un verrou par
    (adapter_name, external_id) — deux commandes simultanées sur le même volet ne partent
    jamais en parallèle vers le protocole."""

    def __init__(self, adapters: dict[str, Adapter]):
        self._adapters = adapters
        self._locks: dict[tuple[str, str], asyncio.Lock] = defaultdict(asyncio.Lock)

    def _adapter(self, adapter_name: str) -> Adapter:
        adapter = self._adapters.get(adapter_name)
        if adapter is None:
            raise UnknownAdapterError(f"Adaptateur inconnu : {adapter_name}")
        return adapter

    async def connect_all(self) -> None:
        for adapter in self._adapters.values():
            await adapter.connect()

    async def discover_devices(self, adapter_name: str) -> list[DiscoveredDevice]:
        return await self._adapter(adapter_name).discover_devices()

    async def _with_device_lock(self, adapter_name: str, external_id: str, coro_factory):
        lock = self._locks[(adapter_name, external_id)]
        try:
            await asyncio.wait_for(lock.acquire(), timeout=LOCK_TIMEOUT_SECONDS)
        except asyncio.TimeoutError as exc:
            raise DeviceBusyError(
                f"Équipement {external_id} déjà en cours de manipulation, réessaie dans un instant"
            ) from exc
        try:
            return await coro_factory()
        finally:
            lock.release()

    async def send_command(
        self, adapter_name: str, external_id: str, command: Command, **params
    ) -> DeviceState:
        adapter = self._adapter(adapter_name)
        return await self._with_device_lock(
            adapter_name, external_id, lambda: adapter.send_command(external_id, command, **params)
        )

    async def get_state(self, adapter_name: str, external_id: str) -> DeviceState:
        adapter = self._adapter(adapter_name)
        return await self._with_device_lock(
            adapter_name, external_id, lambda: adapter.get_state(external_id)
        )
