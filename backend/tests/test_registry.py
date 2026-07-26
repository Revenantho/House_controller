import asyncio

import pytest

from app.adapters.fake.adapter import FakeAdapter
from app.core.commands import Command
from app.core import registry as registry_module
from app.core.registry import AdapterRegistry, DeviceBusyError, UnknownAdapterError


@pytest.fixture()
def registry():
    return AdapterRegistry({"fake": FakeAdapter()})


async def test_send_command_changes_state(registry: AdapterRegistry):
    state = await registry.send_command("fake", "fake-porte-garage", Command.OPEN)
    assert state.is_open is True
    assert state.position == 100


async def test_unknown_adapter_raises(registry: AdapterRegistry):
    with pytest.raises(UnknownAdapterError):
        await registry.send_command("does-not-exist", "whatever", Command.OPEN)


async def test_concurrent_commands_on_same_device_are_serialized(registry: AdapterRegistry):
    """Deux commandes quasi simultanées sur le même équipement ne doivent jamais partir
    en parallèle vers l'adaptateur — exactement le scénario de concurrence évoqué
    (deux comptes cliquant sur le même volet à quelques centaines de ms d'écart)."""
    order: list[str] = []

    class TrackingAdapter(FakeAdapter):
        async def send_command(self, external_id, command, **params):
            order.append(f"start-{command.value}")
            result = await super().send_command(external_id, command, **params)
            order.append(f"end-{command.value}")
            return result

    tracked_registry = AdapterRegistry({"fake": TrackingAdapter()})
    await asyncio.gather(
        tracked_registry.send_command("fake", "fake-volet-salon", Command.OPEN),
        tracked_registry.send_command("fake", "fake-volet-salon", Command.CLOSE),
    )

    # Si les commandes étaient parallèles, on verrait start/start avant les end. Le verrou
    # par device_id garantit qu'un "end" arrive toujours avant le "start" suivant.
    assert order in (
        ["start-OPEN", "end-OPEN", "start-CLOSE", "end-CLOSE"],
        ["start-CLOSE", "end-CLOSE", "start-OPEN", "end-OPEN"],
    )


async def test_device_busy_error_when_lock_timeout_too_short(monkeypatch, registry: AdapterRegistry):
    monkeypatch.setattr(registry_module, "LOCK_TIMEOUT_SECONDS", 0.05)

    async def slow_second_call():
        await asyncio.sleep(0.05)  # laisse le premier appel prendre le verrou en premier
        with pytest.raises(DeviceBusyError):
            await registry.send_command("fake", "fake-volet-salon", Command.CLOSE)

    await asyncio.gather(
        registry.send_command("fake", "fake-volet-salon", Command.OPEN),
        slow_second_call(),
    )
