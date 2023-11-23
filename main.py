import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import json
from datetime import datetime
from langchain.llms.replicate import Replicate
from langchain.vectorstores.chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from decouple import config
from langchain.embeddings import HuggingFaceEmbeddings
import chromadb
from pymongo.cursor import Cursor
from langchain.document_loaders.mongodb import MongodbLoader
from src.logic import get_all_object_data, get_one_object_data
from src.logic import insert_one_object_data, insert_many_object_data
from src.logic import patch_one_object_data, patch_many_object_data
from src.logic import put_one_object_data, put_many_object_data
from src.logic import delete_one_object_data, delete_many_object_data
from src.logic import continuous_ping

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

class ChatParams(BaseModel):
    database: str
    collection: str
    message: str
    type: str

# Get all configuration/device/monitoring objects
@app.post("/configuration/all/")
@app.post("/monitoring/all/")
@app.post("/devices/all/")
@app.post("/chat/all/")
async def get_all(params: DeviceParams):
    data = get_all_object_data(params.database, params.collection)
    if data is None:
        raise HTTPException(status_code=404, detail="Objects not found")
    return {"data":data}

# async def make_continous_ping(background_tasks: BackgroundTasks):
#     target_addresses = ["192.168.254.2", "10.10.5.2", "10.10.5.4", "10.10.5.10", "10.10.5.12","10.10.5.26", "10.10.5.28"]
#     background_tasks.add_task(continuous_ping(target_addresses))
#     return {"message": "Ping of IPs is running in the background"}

# Get one configuration/device/monitoring object
@app.post("/configuration/{id}/")
@app.post("/monitoring/{id}/")
@app.post("/device/{id}/")
async def get_single(id: str, params: DeviceParams):
    data = get_one_object_data(params.database, params.collection, id)
    if data is None:
        raise HTTPException(status_code=404, detail="Object not found")
    return {'data': data}

# Add one configuration object
@app.post("/configuration/add/")
async def insert_single_configuration(params: DeviceParams, configuration: list):

    data = insert_one_object_data(params.database, params.collection, configuration)
    if data is None:
        raise HTTPException(status_code=500, detail="Object not inserted")
    return {'data': data}

# Add one monitoring object
@app.post("/monitoring/add/")
async def insert_single_monitoring(params: DeviceParams, ip: str, status: int):
    post = {
        'ip address': ip,
        'date': datetime.now() + timedelta(hours=3),
        'status': status
    }

    data = insert_one_object_data(params.database, params.collection, post)
    if data is None:
        raise HTTPException(status_code=500, detail="Object not inserted")
    return {'data': data}

# Add one device object
@app.post("/device/add/")
async def insert_single_device(params: DeviceParams, mac_address: str, type: str, manufacturer: str):
    post = {
        'mac address': mac_address,
        'type': type,
        'manufacturer': manufacturer,
        'date': datetime.now() + timedelta(hours=3),
    }

    data = insert_one_object_data(params.database, params.collection, post)
    if data is None:
        raise HTTPException(status_code=500, detail="Object not inserted")
    return {'data': data}

@app.post("/chat/add/")
async def insert_single_chat(params: ChatParams):
    post = {
        'type': params.type,
        'message': params.message,
        'date': datetime.now() + timedelta(hours=3),
    }

    data = insert_one_object_data(params.database, params.collection, post)
    if data is None:
        raise HTTPException(status_code=500, detail="Object not inserted")
    llama_response = await chat_with_json_data(params.database, "monitoring", params.message)
    return {'message': llama_response, "date": datetime.now() + timedelta(hours=3)}

# Add multiple configuration/device/monitoring objects
@app.post("/configuration/add_many/")
async def insert_multiple(params: DeviceParams, objects: list):

    inserted_objects = insert_many_object_data(params.database, params.collection, objects)
    if inserted_objects is None:
        raise HTTPException(status_code=500, detail="Objects not inserted")
    return {'data': inserted_objects}

# Add multiple configuration/device/monitoring objects
@app.post("/monitoring/add_many/")
async def insert_multiple(params: DeviceParams, objects: list):
    insert_objects = [
        {
            'ip address': obj['ip'],
            'date': datetime.now() + timedelta(hours=3),
            'status': obj['status']
        }
        for obj in objects
    ]

    inserted_objects = insert_many_object_data(params.database, params.collection, insert_objects)
    if inserted_objects is None:
        raise HTTPException(status_code=500, detail="Objects not inserted")
    return {'data': inserted_objects}

# Add multiple device objects
@app.post("/device/add_many/")
async def insert_multiple_devices(params: DeviceParams, objects: list):
    insert_objects = [
        {
            'mac address': obj['mac_address'],
            'type': obj['type'],
            'manufacturer': obj['manufacturer'],
            'date': datetime.now() + timedelta(hours=3),
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

async def chat_with_json_data(db_name, collection_name, message):
    try:
        # Connect to MongoDB and the collection
        connection_string = "mongodb://localhost:27017/"
        filter_criteria = {}

        loader = MongodbLoader(connection_string=connection_string,
                              db_name=db_name,
                              collection_name=collection_name,
                              filter_criteria=filter_criteria)
        
        data = await loader.aload()

        # Replicate API token
        os.environ['REPLICATE_API_TOKEN'] = config('REPLICATE_API_TOKEN')

        # Get documents from MongoDB

        # Split the documents into smaller chunks for processing
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(data)

        # Use ChromDB embeddings for transforming text into numerical vectors
        embeddings = HuggingFaceEmbeddings()

        # Set up ChromaDB
        chroma_client = chromadb.Client()
        # chroma_client.delete_collection("my_collection")
        chroma_client.get_or_create_collection(name="monitoring_vector_database")

        # Set up the ChromaDB vector database
        collection_name = "monitoring_vector_database"
        vectordb = Chroma.from_documents(texts, embeddings, collection_name=collection_name)

        # Initialize Replicate Llama2 Model
        llm = Replicate(
            model="a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5",
            model_kwargs={"temperature": 0.75, "max_length": 3000}
        )

        # Set up the Conversational Retrieval Chain
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm,
            vectordb.as_retriever(search_kwargs={'k': 2}),
            return_source_documents=True
        )

        # Use a dictionary for the filter criteria
        filter_criteria = {"type": "recipient"}

        # Convert the filter criteria to a JSON string
        filter_str = json.dumps(filter_criteria)

        # Use the filter string in the find method
        chat_history_list = collection_name.find(filter_str)

        # Check if chat_history_list is iterable (a list or cursor), and handle accordingly
        if isinstance(chat_history_list, (list, Cursor)):
            # Create chat history using a generator expression
            chat_history = ((chat["query"], chat["result"]) for chat in chat_history_list if chat_history_list is not None)
        else:
            # Handle the case where chat_history_list is not iterable
            chat_history = ()

        query = str(message)
        result = qa_chain({'question': query, 'chat_history': chat_history})

        post = {
            "query": query,
            "result": str(result["answer"]),
            "type": "recipient",
            "date": datetime.now() + timedelta(hours=3)
        }
        print(post)
        # Insert chat_obj into the collection and await the result
        chat_obj = insert_one_object_data("test", "chat", post)
        print(chat_obj)
        if not chat_obj:
            raise HTTPException(status_code=500, detail="Chat object not inserted")

        return post["result"]

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An error occurred while processing the request")

if __name__ == "__main__":
    uvicorn.run(app, port=8080, host="0.0.0.0")