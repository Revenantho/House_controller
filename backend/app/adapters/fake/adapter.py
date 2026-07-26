import asyncio

from app.core.adapter import Adapter, DeviceState, DiscoveredDevice
from app.core.commands import Command, DeviceType

ADAPTER_NAME = "fake"

# Équipements simulés en mémoire, alignés sur les mocks déjà utilisés côté frontend
# (mêmes noms/types) pour que le comportement observé soit cohérent des deux côtés.
_SEED_DEVICES: list[DiscoveredDevice] = [
    DiscoveredDevice(
        external_id="fake-volet-salon",
        name="Volet salon",
        device_type=DeviceType.ROLLER_SHUTTER,
        supported_commands=[Command.OPEN, Command.CLOSE, Command.STOP],
        state=DeviceState(is_open=True, position=100, raw={}),
    ),
    DiscoveredDevice(
        external_id="fake-porte-garage",
        name="Porte de garage",
        device_type=DeviceType.GARAGE_DOOR,
        supported_commands=[Command.OPEN, Command.CLOSE, Command.STOP],
        state=DeviceState(is_open=False, position=0, raw={}),
    ),
    DiscoveredDevice(
        external_id="fake-volet-chambre1",
        name="Volet chambre 1",
        device_type=DeviceType.ROLLER_SHUTTER,
        supported_commands=[Command.OPEN, Command.CLOSE, Command.STOP],
        state=DeviceState(is_open=True, position=80, raw={}),
    ),
]

# Simule la latence réseau d'un vrai protocole radio/cloud (Overkiz met couramment
# quelques centaines de ms à confirmer une commande) — utile pour observer le
# comportement de verrouillage par équipement (AdapterRegistry) plutôt qu'un retour instantané.
SIMULATED_LATENCY_SECONDS = 0.3


class FakeAdapter(Adapter):
    """Adaptateur factice : aucun matériel Somfy réel, aucun appel réseau. Implémente le
    même contrat Adapter que le futur OverkizAdapter, pour tester le reste du backend
    (registry, verrous, API, WebSocket) sans dépendre d'un compte Overkiz ou d'une box TaHoma."""

    def __init__(self) -> None:
        self._devices: dict[str, DiscoveredDevice] = {d.external_id: d for d in _SEED_DEVICES}
        self._connected = False

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    async def discover_devices(self) -> list[DiscoveredDevice]:
        return list(self._devices.values())

    async def send_command(self, external_id: str, command: Command, **params) -> DeviceState:
        await asyncio.sleep(SIMULATED_LATENCY_SECONDS)
        device = self._devices.get(external_id)
        if device is None:
            raise KeyError(f"Équipement inconnu de l'adaptateur factice : {external_id}")

        state = device.state
        if command == Command.OPEN:
            state.is_open, state.position = True, 100
        elif command == Command.CLOSE:
            state.is_open, state.position = False, 0
        elif command == Command.SET_POSITION:
            position = int(params.get("position", state.position or 0))
            state.position = position
            state.is_open = position > 0
        # STOP : pas de changement d'état simulé (la vraie box Overkiz laisse la position telle quelle)
        return state

    async def get_state(self, external_id: str) -> DeviceState:
        device = self._devices.get(external_id)
        if device is None:
            raise KeyError(f"Équipement inconnu de l'adaptateur factice : {external_id}")
        return device.state
