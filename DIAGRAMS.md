# Domotique — Diagrammes de classes et de séquence

Voir `SPEC.md` pour la présentation fonctionnelle. Ces diagrammes sont en Mermaid — lisibles directement sur GitHub, dans VS Code (extension Markdown Preview Mermaid), ou via n'importe quel rendu Mermaid.

## Diagramme de classes — architecture adaptateurs (`backend/app/core/` + `backend/app/adapters/`)

```mermaid
classDiagram
    class Adapter {
        <<abstract>>
        +connect()
        +disconnect()
        +discover_devices() DiscoveredDevice[]
        +send_command(external_id, command, params) DeviceState
        +get_state(external_id) DeviceState
    }
    class FakeAdapter {
        +connect()
        +disconnect()
        +discover_devices()
        +send_command()
        +get_state()
    }
    class OverkizAdapter {
        <<à venir>>
        +connect()
        +disconnect()
        +discover_devices()
        +send_command()
        +get_state()
    }
    note for FakeAdapter "Équipements simulés en mémoire, aucun matériel réel"
    note for OverkizAdapter "Pilotera une vraie box TaHoma via la librairie pyoverkiz"
    class AdapterRegistry {
        -adapters : Dict
        -locks : Dict
        +send_command(adapter_name, external_id, command)
        +get_state(adapter_name, external_id)
        +discover_devices(adapter_name)
    }
    class DeviceState {
        +is_open : bool
        +position : int
        +raw : dict
    }
    class DiscoveredDevice {
        +external_id : str
        +name : str
        +device_type : DeviceType
        +supported_commands : Command[]
        +state : DeviceState
    }

    Adapter <|.. FakeAdapter : implémente
    Adapter <|.. OverkizAdapter : implémentera
    AdapterRegistry o-- Adapter : orchestre (1 par protocole)
    Adapter ..> DeviceState : retourne
    Adapter ..> DiscoveredDevice : retourne
```

**Point clé** : `AdapterRegistry` et tout le reste du backend ne connaissent que `Adapter` — jamais `FakeAdapter` ni `OverkizAdapter` directement. Ajouter un protocole = ajouter une classe qui implémente `Adapter`, rien d'autre à modifier.

## Diagramme de classes — modèle de données (`backend/app/models.py`)

```mermaid
classDiagram
    class User {
        +id : str
        +username : str
        +password_hash : str
        +created_at : datetime
    }
    class Floor {
        +id : str
        +name : str
        +display_order : int
        +plan_image_path : str
    }
    class Room {
        +id : str
        +floor_id : str
        +name : str
        +zone_shape : ZonePoint[]
    }
    class Device {
        +id : str
        +name : str
        +device_type : DeviceType
        +room_id : str
        +adapter_name : str
        +external_id : str
        +supported_commands : Command[]
        +last_state : dict
        +last_synced_at : datetime
    }
    class Scenario {
        +id : str
        +name : str
        +enabled : bool
        +days_of_week : int[]
        +time : str
    }
    class ScenarioAction {
        +id : str
        +scenario_id : str
        +device_id : str
        +command : Command
        +params : dict
        +order : int
    }

    Floor "1" --> "*" Room : contient
    Room "1" --> "*" Device : contient (optionnel)
    Scenario "1" --> "*" ScenarioAction : déclenche
    ScenarioAction "*" --> "1" Device : cible
```

**Point clé** : `Device.room_id` est nullable (un équipement découvert peut ne pas encore être rangé dans une pièce) ; `Device.adapter_name` + `Device.external_id` font le lien entre l'équipement tel que connu en base et l'équipement tel que piloté par l'adaptateur.

## Diagramme de séquence — connexion + chargement de la vue Pièces

```mermaid
sequenceDiagram
    participant U as Utilisateur (navigateur)
    participant F as Frontend (React)
    participant A as API /auth
    participant DB as Base SQLite

    U->>F: saisit identifiant / mot de passe
    F->>A: POST /api/auth/login
    A->>DB: SELECT user WHERE username = ...
    DB-->>A: password_hash
    A->>A: vérifie le mot de passe (Argon2)
    A-->>F: 200 OK + cookie de session (HttpOnly)
    Note over F: login ne bloque pas sur l'état des équipements
    F->>A: GET /api/devices
    A-->>F: équipements + last_state en cache
    F-->>U: affiche la vue Pièces avec l'état connu
```

## Diagramme de séquence — envoi d'une commande (verrouillage + WebSocket)

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant F as Frontend
    participant API as API /devices/{id}/command
    participant R as AdapterRegistry
    participant AD as Adapter (Fake ou Overkiz)
    participant WS as Clients WebSocket

    U->>F: clique "Ouvrir"
    F->>API: POST /devices/{id}/command {command: OPEN}
    API->>R: send_command(adapter_name, external_id, OPEN)
    R->>R: acquiert le verrou de l'équipement (asyncio.Lock)
    R->>AD: send_command(external_id, OPEN)
    AD-->>R: DeviceState mis à jour
    R->>R: libère le verrou
    R-->>API: DeviceState
    API->>API: persiste last_state / last_synced_at en base
    API-->>F: 200 OK + Device à jour
    API->>WS: broadcast(Device à jour)
    WS-->>F: message WebSocket (tous les clients connectés)
    F-->>U: bouton et état mis à jour
```

## Diagramme de séquence — deux commandes concurrentes sur le même équipement

Illustre le comportement de verrouillage : deux utilisateurs cliquant sur le même équipement à quelques centaines de millisecondes d'écart ne partent jamais en parallèle vers l'adaptateur.

```mermaid
sequenceDiagram
    participant UA as Utilisateur A
    participant UB as Utilisateur B
    participant API as API
    participant R as AdapterRegistry
    participant AD as Adapter

    UA->>API: POST commande OPEN
    API->>R: send_command(..., OPEN)
    R->>R: acquiert le verrou (libre)
    R->>AD: send_command(OPEN)

    UB->>API: POST commande CLOSE (pendant que A est en cours)
    API->>R: send_command(..., CLOSE)
    R->>R: tente d'acquérir le verrou (déjà pris par A)
    Note over R: attend jusqu'à LOCK_TIMEOUT_SECONDS

    AD-->>R: état après OPEN (fin du traitement de A)
    R->>R: libère le verrou
    R-->>API: 200 OK pour A

    alt le verrou se libère avant le timeout de B
        R->>AD: send_command(CLOSE)
        AD-->>R: état après CLOSE
        R-->>API: 200 OK pour B
    else le timeout de B expire avant
        R-->>API: DeviceBusyError
        API-->>UB: 409 Conflict ("équipement déjà en cours de manipulation")
    end
```
