import json
from pathlib import Path

from sqlalchemy.orm import Session

from . import models
from .adapters.fake.adapter import ADAPTER_NAME as FAKE_ADAPTER_NAME
from .core.commands import Command, DeviceType
from .security import hash_password

DEV_PASSWORD = "password"  # compte de démo uniquement, cf. README backend

FLOORPLANS_DIR = Path(__file__).parent / "floorplans"

# Fichier de config -> device à créer dans cette pièce (nom du device, type, protocole).
# Sert uniquement au jalon "backend factice" : le jour où un vrai adaptateur (Overkiz...)
# remplace FakeAdapter, ce mapping vient du vrai inventaire d'équipements, pas d'un seed statique.
_DEVICES_BY_ROOM_NAME = {
    "Séjour": ("Volet séjour", DeviceType.ROLLER_SHUTTER, "fake-volet-salon"),
    "Garage": ("Porte de garage", DeviceType.GARAGE_DOOR, "fake-porte-garage"),
    "Chambre 1": ("Volet chambre 1", DeviceType.ROLLER_SHUTTER, "fake-volet-chambre1"),
}


def _load_floorplan_configs() -> list[dict]:
    configs = []
    for path in sorted(FLOORPLANS_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            configs.append(json.load(f))
    return configs


def seed_if_empty(db: Session) -> None:
    if db.query(models.User).count() > 0:
        return

    for username in ("alice", "bob", "carol"):
        db.add(models.User(username=username, password_hash=hash_password(DEV_PASSWORD)))

    devices_by_name: dict[str, models.Device] = {}

    for config in _load_floorplan_configs():
        floor = models.Floor(
            name=config["floor_name"],
            display_order=config.get("display_order", 0),
            plan_image_path=config.get("image_path"),
        )
        db.add(floor)
        db.flush()

        for room_config in config.get("rooms", []):
            room = models.Room(
                floor_id=floor.id,
                name=room_config["name"],
                zone_shape=room_config["zone_shape"],
            )
            db.add(room)
            db.flush()

            device_info = _DEVICES_BY_ROOM_NAME.get(room.name)
            if device_info:
                name, device_type, external_id = device_info
                device = models.Device(
                    name=name,
                    device_type=device_type,
                    room_id=room.id,
                    adapter_name=FAKE_ADAPTER_NAME,
                    external_id=external_id,
                    supported_commands=[Command.OPEN, Command.CLOSE, Command.STOP],
                )
                db.add(device)
                db.flush()
                devices_by_name[name] = device

    # Étage sans plan réel fourni pour l'instant — reste vide jusqu'à ce qu'un fichier de
    # config (ex: floorplans/etage1.json) soit ajouté, cf. tâche différée sur les plans.
    if not db.query(models.Floor).filter(models.Floor.name == "1er étage").first():
        db.add(models.Floor(name="1er étage", display_order=99))

    db.flush()

    chambre1_device = devices_by_name.get("Volet chambre 1")
    if chambre1_device:
        scenario = models.Scenario(name="Réveil", enabled=True, days_of_week=[1, 2, 3, 4, 5], time="07:00")
        db.add(scenario)
        db.flush()
        db.add(
            models.ScenarioAction(
                scenario_id=scenario.id,
                device_id=chambre1_device.id,
                command=Command.OPEN,
                params={},
                order=0,
            )
        )

    db.commit()
