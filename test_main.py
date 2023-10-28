from fastapi.testclient import TestClient
from main import app, HTTPException
from pydantic import BaseModel

client = TestClient(app)

class Item(BaseModel):
    _id: str
    ip_address: str
    date: str
    status: int

params = {
        "database": "your_database",
        "collection": "fake_collection"
    }

def test_get_all_configurations():
    response = client.post("/configuration/all/", json=params)
    assert response.status_code == 200
    data = response.json()
    assert data["data"] is not None

def test_get_all_monitoring():
    response = client.post("/monitoring/all/", json=params)
    assert response.status_code == 200
    data = response.json()
    assert data["data"] is not None

def test_get_all_devices():
    response = client.post("/devices/all/", json=params)
    assert response.status_code == 200
    data = response.json()
    assert data["data"] is not None

def test_get_all_objects_not_found():
    params = {
        "database": "nonexistent_db",
        "collection": "nonexistent_collection"
    }
    response = client.post("/devices/all/", json=params)
    assert response.status_code == 404

def test_get_one_device():
    response = client.post("/device/{id}/", json=params)
    assert response.status_code == 200
    assert response.json() is not None

def test_get_one_device_not_found():
    response = client.post("/device/999/", json=params)
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Object not found"}

