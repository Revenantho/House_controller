# Domotique — Spécification et comportement

## Objectif

Hub domotique auto-hébergé pour piloter les équipements de la maison depuis une page web (mobile + PC), sans app native. Premier équipement visé : volets roulants et porte de garage Somfy, via une box TaHoma Switch (protocole Overkiz). Le logiciel est conçu pour être **modulable** : un nouveau protocole ou une nouvelle marque d'équipement doit pouvoir s'ajouter sans réécrire le cœur de l'application.

Accès prévu depuis l'extérieur : tunnel VPN WireGuard (natif sur la Freebox Pop S de l'utilisateur) + nom de domaine dynamique Free — pas d'ouverture de port sur le routeur.

## Périmètre actuel de ce dépôt

| Partie | État |
|---|---|
| `frontend/` | IHM complète (connexion, vue pièces, vue équipements, scénarios en lecture, configuration en lecture) branchée sur une vraie API HTTP + WebSocket |
| `backend/` | API FastAPI réelle (auth, modèle de données SQLite, verrouillage par équipement, WebSocket), mais adossée à un **`FakeAdapter`** qui simule des équipements en mémoire — aucun vrai Somfy/TaHoma n'est encore piloté |
| Adaptateur Somfy/Overkiz réel | Pas encore implémenté (prochaine étape) |
| Moteur de scénarios (exécution planifiée) | Pas encore implémenté (scénarios visibles mais non exécutés) |

Le `FakeAdapter` respecte exactement le même contrat (`Adapter`, cf. `backend/app/core/adapter.py`) que le futur adaptateur Overkiz. Remplacer l'un par l'autre ne touche à rien d'autre dans le code — c'est le test concret de l'architecture modulable.

## Fonctionnalités

### Authentification
Session serveur (cookie `HttpOnly`, mot de passe hashé Argon2). Trois comptes de démonstration : `alice` / `bob` / `carol`, mot de passe `password` (cf. `backend/app/seed.py` — à changer avant tout usage réel).

### Vue Pièces
Plan de la maison par étage (switch RDC / 1er étage), avec des zones cliquables représentant les pièces (polygones stockés en pourcentage de la surface de l'image, donc responsive sans recalcul). Cliquer une pièce affiche ses équipements et permet d'envoyer une commande (Ouvrir / Fermer / Stop).

### Vue Équipements
Les mêmes équipements, mais groupés par type plutôt que par pièce — même composant d'affichage (`DeviceCard`) que la vue Pièces, juste un regroupement différent sur le même modèle de données.

### Scénarios
Affichage des scénarios existants (nom, jours, heure, nombre d'actions). La création/édition et surtout **l'exécution planifiée** (scheduler) ne sont pas encore implémentées — sujet explicitement différé.

### Configuration de la maison
Écran de consultation des étages/pièces/équipements. L'édition (CRUD complet, dessin des zones à la souris) n'est pas encore branchée côté IHM, bien que l'API backend expose déjà les endpoints nécessaires.

## Comportements à connaître

- **Rafraîchissement au login** : la connexion ne bloque pas en attendant l'état de tous les équipements — l'IHM affiche l'état en cache (`lastState`/`lastSyncedAt`) immédiatement, les mises à jour arrivent ensuite via WebSocket.
- **Verrouillage par équipement** : deux commandes quasi simultanées sur le même équipement ne partent jamais en parallèle vers l'adaptateur (verrou `asyncio.Lock` par équipement, timeout court avec erreur explicite plutôt qu'une attente bloquante — cf. `backend/app/core/registry.py`).
- **Latence simulée** : le `FakeAdapter` introduit un délai artificiel (~300ms) sur les commandes, pour observer un comportement réaliste (et le verrouillage) même sans vrai matériel.
- **WebSocket** : sert surtout à confirmer une commande envoyée depuis l'IHM, pas à un vrai temps réel physique — un adaptateur réel comme Overkiz ne rafraîchit lui-même l'état que toutes les ~30s côté fournisseur.

## Lancer le projet

```bash
# Backend
cd backend
python -m venv .venv && .venv\Scripts\activate  # ou l'équivalent de votre shell
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Tests backend
pytest

# Frontend (dans un autre terminal)
cd frontend
npm install
npm run dev
```

Le frontend (port 5173) proxifie `/api` vers le backend (port 8000) — voir `frontend/vite.config.ts`. Ouvrir `http://localhost:5173`, se connecter avec un des comptes de démo.

## Pour aller plus loin

Voir `DIAGRAMS.md` pour le diagramme de classes et les diagrammes de séquence. Le plan d'architecture complet (décisions, alternatives écartées) est conservé séparément dans les notes de planification de la session ayant construit ce projet.
