from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Pousse les changements d'état aux clients connectés. Utilisé surtout pour la
    confirmation quasi-instantanée après une commande envoyée depuis l'IHM — pas pour
    un vrai temps réel physique, cf. plan (l'état d'un adaptateur réel type Overkiz ne
    se rafraîchit lui-même que toutes les ~30s côté fournisseur)."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def broadcast(self, payload: dict) -> None:
        stale: list[WebSocket] = []
        for connection in self._connections:
            try:
                await connection.send_json(payload)
            except Exception:
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/api/ws/state")
async def websocket_state(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Le client n'envoie rien pour l'instant ; on garde la connexion ouverte
            # pour recevoir les broadcasts déclenchés par les commandes.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
