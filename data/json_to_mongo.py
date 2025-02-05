import json
from pymongo import MongoClient, InsertOne
import numpy as np


def cosine_similarity(a, b):
    if len(a) > len(b):
        b = np.pad(b, (0, len(a) - len(b)), 'constant')
    elif len(b) > len(a):
        a = np.pad(a, (0, len(b) - len(a)), 'constant')
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

client = MongoClient(
    "MONGODB URI"
    )
db = client.myDatabase
collection = db.myCollection

requesting = []

with open(r"/master_enriched_lite.json") as f:
    json_data = json.load(f)
    if isinstance(json_data, list):
        for obj in json_data:
            requesting.append(InsertOne(obj))
    else:
        requesting.append(InsertOne(json_data))
        
result = collection.bulk_write(requesting)
client.close()
