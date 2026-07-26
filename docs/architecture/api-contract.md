# Architecture — contrat API front/back

## Où ça vit

- `backend/app/routers/` — un fichier par ressource (`auth.py`, `floors.py`, `rooms.py`, `devices.py`, `scenarios.py`, `ws.py`), montés dans `backend/app/main.py`.
- `backend/app/schemas.py` — `CamelModel` (base Pydantic avec `alias_generator=to_camel`) : tous les schémas de requête/réponse en héritent, c'est le seul endroit où la conversion camelCase↔snake_case se fait. Ne jamais construire de réponse JSON à la main dans un router.
- `backend/app/deps.py` — `get_current_user` (dépendance FastAPI réutilisée sur toutes les routes protégées) et `get_registry` (accès à l'`AdapterRegistry` singleton).
- `frontend/src/api/*.ts` — un fichier par ressource, chacun n'exporte que des fonctions typées (`getDevices`, `sendCommand`...), jamais d'appel `fetch` direct ailleurs dans le frontend.
- `frontend/src/api/client.ts` — wrapper `apiFetch` unique (base URL, `credentials: 'include'`, gestion d'erreur `ApiError`).
- `frontend/src/ws/useDeviceStateSocket.ts` + `frontend/app/routers/ws.py::ConnectionManager` — le pont WebSocket, découplé du reste (un hook côté client, un gestionnaire de connexions côté serveur).

## Ce qui NE change PAS pour une nouvelle route

- Le préfixe `/api`, la session cookie, et `CamelModel` s'appliquent automatiquement à toute nouvelle route ajoutée dans `routers/` — pas de configuration par route à dupliquer.
- Le proxy Vite (`frontend/vite.config.ts`) route déjà `/api` et `/static` vers le backend ; une nouvelle route backend est immédiatement accessible côté frontend sans configuration supplémentaire.
