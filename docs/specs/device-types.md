# Spécification — types d'équipements

Comportement attendu pour chaque type d'équipement supporté par le hub. Un type d'équipement définit : les commandes qu'il accepte, la forme de son état, et ses cas limites. Le cœur du logiciel (`core/`) ne connaît que ce contrat générique — jamais un type précis.

## Volet roulant (`ROLLER_SHUTTER`)

- **Commandes** : `OPEN` (ouvre complètement), `CLOSE` (ferme complètement), `STOP` (arrête le mouvement en cours, ne change pas la position connue), `SET_POSITION` (position cible 0-100, 0 = fermé, 100 = ouvert).
- **État** : `is_open` (bool, dérivé de la position : `position > 0`), `position` (0-100).
- **Cas limites** :
  - `SET_POSITION` avec une valeur hors 0-100 doit être rejetée (422), pas silencieusement bornée côté serveur.
  - `STOP` ne modifie pas `position`/`is_open` dans l'adaptateur factice (comportement réaliste : on ne connaît pas la position exacte après un arrêt en cours de mouvement sur un volet réel sans capteur).

## Porte de garage (`GARAGE_DOOR`)

- **Commandes** : `OPEN`, `CLOSE`, `STOP` — mêmes règles que le volet roulant, pas de `SET_POSITION` (pas de position intermédiaire pilotée dans ce jalon).
- **État** : `is_open`, `position` (0 ou 100 uniquement dans les faits, mais le champ reste générique).

## Cas de tests à couvrir (existants)

- `test_send_command_changes_state` — commande simple change bien l'état.
- `test_concurrent_commands_on_same_device_are_serialized` — deux commandes quasi simultanées sur le même équipement ne partent jamais en parallèle vers l'adaptateur.
- `test_device_busy_error_when_lock_timeout_too_short` — verrou occupé → erreur explicite, pas d'attente indéfinie.
- `test_unsupported_command_rejected` — une commande hors de `supportedCommands` du device est refusée (422).

*(Les futurs types — Lumière, Ventilateur — seront ajoutés ici avec leur propre section, au moment où `instruction_pilotage_device.md` sera traité.)*
