import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from src.logic import get_all_object_data, get_one_object_data
from src.logic import insert_one_object_data, insert_many_object_data
from src.logic import patch_one_object_data, patch_many_object_data
from src.logic import put_one_object_data, put_many_object_data
from src.logic import delete_one_object_data, delete_many_object_data
from src.logic import ping_host

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []

class DeviceParams(BaseModel):
    database: str
    collection: str

# Get all configuration/device/monitoring objects
@app.post("/configuration/all/")
@app.post("/monitoring/all/")
@app.post("/devices/all/")
async def get_all(params: DeviceParams):
    data = get_all_object_data(params.database, params.collection)
    if data is None:
        raise HTTPException(status_code=404, detail="Objects not found")
    return {"data":data}

# Get one configuration/device/monitoring object
@app.post("/configuration/{id}/")
@app.post("/monitoring/{id}/")
@app.post("/device/{id}/")
async def get_single(id: str, params: DeviceParams):
    data = get_one_object_data(params.database, params.collection, id)
    if data is None:
        raise HTTPException(status_code=404, detail="Object not found")
    return {'data': data}

# Add one configuration/device/monitoring object
@app.post("/configuration/add/")
@app.post("/monitoring/add/")
@app.post("/device/add/")
async def insert_single(params: DeviceParams, ip: str, status: int):
    post = {
        'ip address': ip,
        'date': datetime.now(),
        'status': status
    }

    data = insert_one_object_data(params.database, params.collection, post)
    if data is None:
        raise HTTPException(status_code=500, detail="Object not inserted")
    return {'data': data}

# Add multiple configuration/device/monitoring objects
@app.post("/configuration/add_many/")
@app.post("/monitoring/add_many/")
@app.post("/device/add_many/")
async def insert_multiple(params: DeviceParams, objects: list):
    insert_objects = [
        {
            'ip address': obj['ip'],
            'date': datetime.now(),
            'status': obj['status']
        }
        for obj in objects
    ]

    inserted_objects = insert_many_object_data(params.database, params.collection, insert_objects)
    if inserted_objects is None:
        raise HTTPException(status_code=500, detail="Objects not inserted")
    return {'data': inserted_objects}

# Patch one configuration/device/monitoring object
@app.patch("/configuration/update/{id}/")
@app.patch("/monitoring/update/{id}/")
@app.patch("/device/update/{id}/")
async def patch_single(id: str, params: DeviceParams):
    data = patch_one_object_data(params.database, params.collection, id)
    if data is None:
        raise HTTPException(status_code=404, detail="Object not found")
    return {'data': data}

# Patch many configuration/device/monitoring objects
@app.patch("/configuration/update_many/")
@app.patch("/monitoring/update_many/")
@app.patch("/device/update_many/")
async def patch_multiple(params: DeviceParams, objects: list):

    patched_objects = patch_many_object_data(params.database, params.collection, objects)
    if patched_objects is None:
        raise HTTPException(status_code=500, detail="Objects not found")
    return {'data': patched_objects}

# Put one configuration/device/monitoring object
@app.put("/configuration/replace/{id}/")
@app.put("/monitoring/replace/{id}/")
@app.put("/device/replace/{id}/")
async def put_single(id: str, params: DeviceParams):
    data = put_one_object_data(params.database, params.collection, id)
    if data is None:
        raise HTTPException(status_code=404, detail="Object not found")
    return {'data': data}

# Put many configuration/device/monitoring objects
@app.put("/configuration/replace_many/")
@app.put("/monitoring/replace_many/")
@app.put("/device/replace_many/")
async def put_multiple(params: DeviceParams, objects: list):

    replaced_objects = put_many_object_data(params.database, params.collection, objects)
    if replaced_objects is None:
        raise HTTPException(status_code=500, detail="Objects not found")
    return {'data': replaced_objects}

# Delete one configuration/device/monitoring object
@app.delete("/configuration/delete/{id}/")
@app.delete("/monitoring/delete/{id}/")
@app.delete("/device/delete/{id}/")
async def delete_single(id: str, params: DeviceParams):
    data = delete_one_object_data(params.database, params.collection, id)
    if data is None:
        raise HTTPException(status_code=404, detail="Object not found")
    return {'data': data}

# Delete many configuration/device/monitoring objects
@app.delete("/configuration/delete_many/")
@app.delete("/monitoring/delete_many/")
@app.delete("/device/delete_many/")
async def delete_multiple(params: DeviceParams, objects: list):

    deleted_objects = delete_many_object_data(params.database, params.collection, objects)
    if deleted_objects is None:
        raise HTTPException(status_code=500, detail="Objects not deleted")
    return {'data': deleted_objects}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        clients.remove(websocket)


def ping_address():
    a, b = ping_host("8.8.8.8")
    print(a, b)

if __name__ == "__main__":
    uvicorn.run(app, port=8080, host="0.0.0.0")