# Spécification — contrat API front/back

Tous les échanges passent par `/api/*` (REST) et `/api/ws/state` (WebSocket). Le frontend envoie/reçoit du camelCase ; le backend traduit en interne vers snake_case (cf. `CamelModel` dans `backend/app/schemas.py`).

## Authentification

- `POST /api/auth/login` — `{username, password}` → `200 {id, username}` + cookie de session `HttpOnly`. `401` si identifiants invalides.
- `POST /api/auth/logout` — `204`, vide la session.
- `GET /api/auth/me` — `200 {id, username}` si connecté, `401` sinon.
- Toutes les autres routes exigent une session valide (`401` sinon).

## Étages / pièces

- `GET /api/floors` — liste triée par `displayOrder`.
- `POST/PATCH/DELETE /api/floors[/{id}]` — CRUD.
- `GET /api/floors/{id}/rooms` — pièces d'un étage, avec `zoneShape` (polygone en % de l'image).
- `POST/PATCH/DELETE /api/rooms[/{id}]` — CRUD.

## Équipements

- `GET /api/devices?room_id=X&type=Y` — liste filtrable (sert les deux vues IHM : par pièce, par type).
- `PATCH /api/devices/{id}` — modifie `name`/`roomId`.
- `POST /api/devices/{id}/command` — `{command, params}` → exécute via `AdapterRegistry`, persiste l'état, diffuse sur le WebSocket. `404` si device inconnu, `422` si commande non supportée par ce device, `409` si l'équipement est déjà en cours de manipulation (verrou).
- `POST /api/devices/discover` — relance la découverte adaptateur, met à jour l'état des devices déjà connus.

## Scénarios

- `GET /api/scenarios` — liste avec leurs actions.
- `POST /api/scenarios` — crée un scénario + ses actions.
- `DELETE /api/scenarios/{id}`.
- Pas encore de moteur d'exécution planifiée (sujet différé).

## WebSocket (`/api/ws/state`)

- Le client se connecte et reçoit, en JSON, chaque `Device` mis à jour après une commande (même format que les réponses REST, camelCase).
- Ne sert pas de canal de commande — le client n'envoie rien d'interprété, seul le serveur pousse.

## Cas de tests à couvrir (existants)

- Auth : login succès/échec, `/me` avec et sans session, logout invalide la session.
- Devices : liste filtrée par type, commande met à jour l'état, commande non supportée → 422, device inconnu → 404.
- Verrouillage : cf. `docs/specs/device-types.md` (les cas de concurrence sont documentés là car ils dépendent du comportement de l'adaptateur, pas juste du contrat HTTP).
