from pymongo import MongoClient
from netmiko import ConnectHandler
from icmplib import ping
from bson import ObjectId
import json
from icmplib import ping
import concurrent.futures
from datetime import datetime, timedelta
from langchain.llms.replicate import Replicate
from langchain.vectorstores.chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from decouple import config
from pymongo import MongoClient
from langchain.embeddings import HuggingFaceEmbeddings
import chromadb
from langchain.document_loaders.mongodb import MongodbLoader

# Connect to MongoDB database
def connect_to_mongodb(database_of_choice, collection_of_choice):
    url = "mongodb://localhost:27017/"
    client = MongoClient(url)
    db = client[database_of_choice]
    collection = db[collection_of_choice]
    return collection

# Get one configuration/device/monitoring object
def get_one_object_data(database, collection, object_id):
    collection = connect_to_mongodb(database, collection)
    try:
        object_id = ObjectId(object_id)
        data = collection.find_one({"_id": object_id})
        data['_id'] = str(data['_id'])
        return data
    except:
        return None

# Get all configuration/device/monitoring objects
def get_all_object_data(database, collection):
    collection = connect_to_mongodb(database, collection)
    try:
        data = list(collection.find())
        for document in data:
            document['_id'] = str(document['_id'])

        return data
    except:
        return None

# Insert one configuration/device/monitoring object
def insert_one_object_data(database, collection, insert_object):
    collection = connect_to_mongodb(database, collection)
    try:
        insert_result = collection.insert_one(insert_object)
        inserted_object = collection.find_one({"_id": insert_result.inserted_id})
        inserted_object['_id'] = str(inserted_object['_id'])
        return inserted_object
    except Exception as e:
        print(e)
        return None

# Insert many configuration/device/monitoring objects
def insert_many_object_data(database, collection, insert_objects):
    collection = connect_to_mongodb(database, collection)
    try:
        result = collection.insert_many(insert_objects)
        inserted_object_ids = result.inserted_ids

        inserted_objects = list(collection.find({"_id": {"$in": inserted_object_ids}}))

        for obj in inserted_objects:
            obj['_id'] = str(obj['_id'])

        return inserted_objects
    except Exception as e:
        print(e)
        return None

# Put (full update) one configuration/device/monitoring object
def put_one_object_data(database, collection, object_id, update_object):
    collection = connect_to_mongodb(database, collection)
    try:
        object_id = ObjectId(object_id)
        result = collection.replace_one({"_id": object_id}, update_object)
        if result.matched_count > 0:
            return "Object updated successfully"
        else:
            return "Object not found"
    except Exception as e:
        print(e)
        return None

# Put (full update) many configuration/device/monitoring objects
def put_many_object_data(database, collection, filter_objects, update_object):
    collection = connect_to_mongodb(database, collection)
    try:
        # Convert the provided IDs to ObjectId
        object_ids = [ObjectId(obj_id) for obj_id in filter_objects]
        result = collection.update_many({"_id": {"$in": object_ids}}, {"$set": update_object})
        if result.matched_count > 0:
            return "Objects updated successfully"
        else:
            return "No objects found to update"
    except Exception as e:
        print(e)
        return None

# Patch (partial update) one configuration/device/monitoring object
def patch_one_object_data(database, collection, object_id, update_object):
    collection = connect_to_mongodb(database, collection)
    try:
        object_id = ObjectId(object_id)
        result = collection.update_one({"_id": object_id}, {"$set": update_object})
        if result.matched_count > 0:
            return "Object updated successfully"
        else:
            return "Object not found"
    except Exception as e:
        print(e)
        return None

# Patch (partial update) many configuration/device/monitoring objects
def patch_many_object_data(database, collection, filter_objects, update_object):
    collection = connect_to_mongodb(database, collection)
    try:
        # Convert the provided IDs to ObjectId
        object_ids = [ObjectId(obj_id) for obj_id in filter_objects]
        result = collection.update_many({"_id": {"$in": object_ids}}, {"$set": update_object})
        if result.matched_count > 0:
            return "Objects updated successfully"
        else:
            return "No objects found to update"
    except Exception as e:
        print(e)
        return None

# Delete one configuration/device/monitoring object
def delete_one_object_data(database, collection, object_id):
    collection = connect_to_mongodb(database, collection)
    try:
        object_id = ObjectId(object_id)
        result = collection.delete_one({"_id": object_id})
        if result.deleted_count > 0:
            return "Object deleted successfully"
        else:
            return "Object not found"
    except Exception as e:
        print(e)
        return None

# Delete many configuration/device/monitoring objects
def delete_many_object_data(database, collection, filter_objects):
    collection = connect_to_mongodb(database, collection)
    try:
        object_ids = [ObjectId(obj_id) for obj_id in filter_objects]
        result = collection.delete_many({"_id": {"$in": object_ids}})
        if result.deleted_count > 0:
            return "Objects deleted successfully"
        else:
            return "No objects found to delete"
    except Exception as e:
        print(e)
        return None

#Monitor address
def ping_host(address):
    try:
        result = ping(address, count=1, privileged=False)
        return (address, result)
    except Exception as e:
        return (address, str(e))

#telnet or ssh to networking device and configure it
def connect_and_configure_device(ip, port, config_commands):
    device = {
    'device_type': 'cisco_ios_telnet',
    'ip': ip,
    'port': port
    }
    
    net_connect = ConnectHandler(**device)
    output = net_connect.send_config_set(config_commands)
    print(output)
    net_connect.disconnect()

# Append new records to the JSON file
def append_record_to_json_file(database, collection, ids):
    try:
        file_path = "j.json"

        existing_data = []

        try:
            with open(file_path, "r") as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            pass

        for object_id in ids:
            returned_object = get_one_object_data(database, collection, object_id)
            existing_data.append(returned_object)

        with open(file_path, "w") as file:
            json.dump(existing_data, file)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def continuous_ping(target_addresses):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            # Adjust max_workers to control the number of parallel pings
            results = list(executor.map(ping_host, target_addresses))

            for address, result in results:
                date = datetime.now() + timedelta(hours=3)
                if result.packet_loss == 0:
                    insert_one_object_data("test", "monitoring", {"ip address": address, "date": date, "status": 1})
                else:
                    insert_one_object_data("test", "monitoring", {"ip address": address, "date": date, "status": 0})