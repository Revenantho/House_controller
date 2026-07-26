from .adapters.fake.adapter import ADAPTER_NAME as FAKE_ADAPTER_NAME
from .adapters.fake.adapter import FakeAdapter
from .core.registry import AdapterRegistry

# Un seul process, un seul registry en mémoire pour toute l'appli — cohérent avec le choix
# "pas de scaling horizontal" du plan (verrou par device_id en mémoire, pas de verrou distribué).
_registry = AdapterRegistry({FAKE_ADAPTER_NAME: FakeAdapter()})


def get_registry() -> AdapterRegistry:
    return _registry
