from icmplib import ping
import concurrent.futures
from pymongo import MongoClient
from datetime import datetime, timedelta
import time

url = "mongodb://localhost:27017"
client = MongoClient(url)
db = client["test"]
collection = db["monitoring"]
i = 0

target_addresses = ["192.168.254.2", "10.10.5.2", "10.10.5.4", "10.10.5.10", "10.10.5.12","10.10.5.26", "10.10.5.28"]

def insertData(ip, date, status):
    status_object = {
        "ip address": ip,
        "date": date,
        "status": status,
    }

    post_result = collection.insert_one(status_object)
    if post_result.acknowledged:
        print("Document inserted with ID:", post_result.inserted_id)
    else:
        print("Insertion failed")

def ping_host(address):
    try:
        result = ping(address, count=1, privileged=False)
        if result.packet_loss == 0:
            insertData(address, datetime.now() + timedelta(hours=3), 1)
        else:
            insertData(address, datetime.now() + timedelta(hours=3), 0)
    except Exception as e:
        insertData(address, datetime.now() + timedelta(hours=3), -1)

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(60):
            results = list(executor.map(ping_host, target_addresses))
            time.sleep(1)
