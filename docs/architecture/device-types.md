# Architecture — types d'équipements

## Où le vocabulaire d'un type d'équipement vit dans le code

- `backend/app/core/commands.py` — `DeviceType` (enum) et `Command` (enum). C'est le seul endroit où un nouveau type/commande se déclare.
- `backend/app/core/adapter.py` — `DeviceState` (dataclass) : champs génériques partagés par tous les types (`is_open`, `position`, `raw`). Un nouveau type qui a besoin d'un champ que les autres n'utilisent pas **ajoute** un champ optionnel plutôt que de réutiliser un champ existant avec un sens différent (ex : ne pas faire porter à `is_open` le sens "allumé" pour une lumière).
- `backend/app/adapters/fake/adapter.py` — `FakeAdapter` : simule le comportement de chaque type en mémoire (utilisé tant qu'aucun vrai protocole n'est branché).
- `backend/app/schemas.py` — `DeviceStateOut`/`DeviceOut` : miroir Pydantic exposé à l'API, doit suivre `DeviceState`.
- `backend/app/routers/devices.py::_apply_state` — sérialise l'état retourné par l'adaptateur vers `Device.last_state` (JSON) ; point à ne pas oublier quand un nouveau champ d'état est ajouté, sinon il n'est jamais persisté.
- `frontend/src/types/device.ts` — miroir TypeScript de `DeviceType`/`Command`/`DeviceState`.
- `frontend/src/components/DeviceCard.tsx` — rendu UI conditionnel selon `supportedCommands` du device (boutons, sliders...).

## Ce qui NE change PAS quand on ajoute un type

- `backend/app/models.py` : `Device.device_type` est une colonne enum stockée en string (`native_enum=False`) et `last_state` est un blob JSON schemaless — ajouter une valeur d'enum ou une clé JSON ne nécessite aucune migration de base de données.
- `core/adapter.py::Adapter` (l'ABC) et `core/registry.py::AdapterRegistry` : le contrat et le verrouillage par équipement sont génériques, jamais spécifiques à un type.
