def test_list_devices_requires_authentication(client):
    response = client.get("/api/devices")
    assert response.status_code == 401


def test_list_devices(logged_in_client):
    response = logged_in_client.get("/api/devices")
    assert response.status_code == 200
    names = {d["name"] for d in response.json()}
    assert {"Volet séjour", "Porte de garage", "Volet chambre 1"} <= names


def test_filter_devices_by_type(logged_in_client):
    response = logged_in_client.get("/api/devices", params={"type": "GARAGE_DOOR"})
    assert response.status_code == 200
    devices = response.json()
    assert len(devices) == 1
    assert devices[0]["deviceType"] == "GARAGE_DOOR"


def test_send_command_updates_state(logged_in_client):
    devices = logged_in_client.get("/api/devices", params={"type": "GARAGE_DOOR"}).json()
    device_id = devices[0]["id"]

    response = logged_in_client.post(f"/api/devices/{device_id}/command", json={"command": "OPEN"})
    assert response.status_code == 200
    body = response.json()
    assert body["lastState"]["isOpen"] is True
    assert body["lastSyncedAt"] is not None


def test_unsupported_command_rejected(logged_in_client, monkeypatch):
    devices = logged_in_client.get("/api/devices", params={"type": "GARAGE_DOOR"}).json()
    device_id = devices[0]["id"]

    response = logged_in_client.post(
        f"/api/devices/{device_id}/command", json={"command": "SET_POSITION", "params": {"position": 50}}
    )
    assert response.status_code == 422


def test_unknown_device_returns_404(logged_in_client):
    response = logged_in_client.post("/api/devices/does-not-exist/command", json={"command": "OPEN"})
    assert response.status_code == 404
