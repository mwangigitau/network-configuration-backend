import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from src.logic import get_all_object_data, get_one_object_data
# from src.logic import insert_one_object_data, insert_many_object_data
# from src.logic import update_one_object_data, update_many_object_data
# from src.logic import put_one_object_data, put_many_object_data
from src.logic import delete_one_object_data, delete_many_object_data

app = FastAPI()

class DeviceParams(BaseModel):
    database: str
    collection: str

# Get all configuration/device/monitoring objects
@app.post("/configuration/all/")
@app.post("/monitoring/all/")
@app.post("/devices/all/")
async def get_all(params: DeviceParams):
    data = get_all_object_data(params.database, params.collection)
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

# # Add one configuration/device/monitoring object
# @app.post("/configuration/add/")
# @app.post("/monitoring/add/")
# @app.post("/device/add/")
# async def insert_single(params: DeviceParams, ip: str, status: int):
#     post = {
#         'ip address': ip,
#         'date': datetime.now(),
#         'status': status
#     }

#     data = insert_one_object_data(params.database, params.collection, post)
#     if data is None:
#         raise HTTPException(status_code=500, detail="Object not inserted")
#     return {'data': data}

# # Add multiple configuration/device/monitoring objects
# @app.post("/configuration/add_many/")
# @app.post("/monitoring/add_many/")
# @app.post("/device/add_many/")
# async def insert_multiple(params: DeviceParams, objects: list):
#     insert_objects = [
#         {
#             'ip address': obj['ip'],
#             'date': datetime.now(),
#             'status': obj['status']
#         }
#         for obj in objects
#     ]

#     inserted_objects = insert_many_object_data(params.database, params.collection, insert_objects)
#     if inserted_objects is None:
#         raise HTTPException(status_code=500, detail="Objects not inserted")
#     return {'data': inserted_objects}

# # Patch one configuration/device/monitoring object
# @app.patch("/configuration/update/{id}/")
# @app.patch("/monitoring/update/{id}/")
# @app.patch("/device/update/{id}/")

# # Patch many configuration/device/monitoring objects
# @app.patch("/configuration/update_many/")
# @app.patch("/monitoring/update_many/")
# @app.patch("/device/update_many/")

# # Put one configuration/device/monitoring object
# @app.put("/configuration/replace/{id}/")
# @app.put("/monitoring/replace/{id}/")
# @app.put("/device/replace/{id}/")

# # Put many configuration/device/monitoring objects
# @app.put("/configuration/replace_many/")
# @app.put("/monitoring/replace_many/")
# @app.put("/device/replace_many/")

# # Delete one configuration/device/monitoring object
# @app.delete("/configuration/delete/{id}/")
# @app.delete("/monitoring/delete/{id}/")
# @app.delete("/device/delete/{id}/")
# async def delete_single(id: str, params: DeviceParams):
#     data = delete_one_object_data(params.database, params.collection, id)
#     if data is None:
#         raise HTTPException(status_code=404, detail="Object not found")
#     return {'data': data}

# # Delete many configuration/device/monitoring objects
# @app.delete("/configuration/delete_many/")
# @app.delete("/monitoring/delete_many/")
# @app.delete("/device/delete_many/")
# async def delete_multiple(params: DeviceParams, objects: list):

#     deleted_objects = delete_many_object_data(params.database, params.collection, objects)
#     if deleted_objects is None:
#         raise HTTPException(status_code=500, detail="Objects not deleted")
#     return {'data': deleted_objects}


# # Get all configuration objects from a specific database and collection using POST
# @app.post("/configurations/all/")
# async def get_all_configurations(params: DeviceParams):
#     data = get_all_object_data(params.database, params.collection)
#     return {"data":data}

# # Get one configuration object from a specific database and collection using POST
# @app.post("/configuration/{id}/")
# async def get_one_configuration(id: str, params: DeviceParams):
#     data = get_one_object_data(params.database, params.collection, id)
#     if data is None:
#         raise HTTPException(status_code=404, detail="Object not found")
#     return {'data': data}

# # Get all monitoring objects from a specific database and collection using POST
# @app.post("/monitoring/all/")
# async def get_all_monitoring(params: DeviceParams):
#     data = get_all_object_data(params.database, params.collection)
#     return {"data":data}

# # Get one monitoring object from a specific database and collection using POST
# @app.post("/monitoring/{id}/")
# async def get_one_monitoring(id: str, params: DeviceParams):
#     data = get_one_object_data(params.database, params.collection, id)
#     print(data)
#     if data is None:
#         raise HTTPException(status_code=404, detail="Object not found")
#     return {'data': data}

# # Add one configuration/device/monitoring object
# @app.post("/configuration/add/")
# async def insert_one_configuration(params: DeviceParams, ip: str, status: int):
#     post = {
#         'ip address': ip,
#         'date': datetime.now(),
#         'status': status
#     }

#     data = insert_one_object_data(params.database, params.collection, post)
#     if data is None:
#         raise HTTPException(status_code=500, detail="Object not inserted")
#     return {'data': data}

# # Add multiple configuration/device/monitoring objects
# @app.post("/configuration/add_many/")
# async def insert_many_configurations(params: DeviceParams, objects: list):
#     insert_objects = [
#         {
#             'ip address': obj['ip'],
#             'date': datetime.now(),
#             'status': obj['status']
#         }
#         for obj in objects
#     ]

#     inserted_objects = insert_many_object_data(params.database, params.collection, insert_objects)
#     if inserted_objects is None:
#         raise HTTPException(status_code=500, detail="Objects not inserted")
#     return {'data': inserted_objects}

# # Add one configuration/device/monitoring object
# @app.post("/configuration/add/")
# async def insert_one_configuration(params: DeviceParams, ip: str, status: int):
#     post = {
#         'ip address': ip,
#         'date': datetime.now(),
#         'status': status
#     }

#     data = insert_one_object_data(params.database, params.collection, post)
#     if data is None:
#         raise HTTPException(status_code=500, detail="Object not inserted")
#     return {'data': data}

# # Add multiple monitoring objects
# @app.post("/monitoring/add_many/")
# async def insert_many_configurations(params: DeviceParams, objects: list):
#     insert_objects = [
#         {
#             'ip address': obj['ip'],
#             'date': datetime.now(),
#             'status': obj['status']
#         }
#         for obj in objects
#     ]

#     inserted_objects = insert_many_object_data(params.database, params.collection, insert_objects)
#     if inserted_objects is None:
#         raise HTTPException(status_code=500, detail="Objects not inserted")
#     return {'data': inserted_objects}

if __name__ == "__main__":
    uvicorn.run(app, port=8080, host="0.0.0.0")

# print(get_all_object_data("test", "students"))
# print(get_one_object_data("test", "students", "65310f812d5b009236d8f697"))