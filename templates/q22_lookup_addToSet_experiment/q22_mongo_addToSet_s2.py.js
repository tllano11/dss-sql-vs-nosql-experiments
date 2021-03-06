#!/bin/python3.6
from pymongo import MongoClient
import time

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client["{{ variables['mongo_db_name'] }}"]
{{ variables['mongo_C'] }} = db.{{ variables['mongo_C'] }}

t0 = time.time()
pipeline = {{ variables['mongo_C'] }}.aggregate([
    {"$match": {
	"c_acctbal": {"$gt": 0.0}
    }},
    {"$project": {
        "_id": 1,
	"c_acctbal": 1,
	"cntrycode": {"$substr":["$c_phone", 0, 2]}
    }},
    {"$match": {
	"cntrycode": {"$in": ['30', '17', '25', '10', '22', '15', '21'] }
    }},
    {"$lookup": {
        "from": "{{ variables['mongo_O'] }}",
        "localField": "_id",
        "foreignField": "o_custkey",
        "as": "c_orders"
    }},
    {"$group": {
	"_id": None,
        "c_acctbals": {"$addToSet": {
            "c_custkey":"$_id", # This distinguishes equal tuples of balance and cntrycode
            "c_acctbal":"$c_acctbal", 
            "cntrycode":"$cntrycode", 
            "num_orders": {"$size":"$c_orders"}
        }},
	"c_acctbal_avg": {"$avg": "$c_acctbal"}
    }},
    {"$unwind": "$c_acctbals"},
    {"$match": {
        "$expr": { "$and":[
            {"$gt":["$c_acctbals.c_acctbal", "$c_acctbal_avg"]}, 
            {"$eq":["$c_acctbals.num_orders", 0]}
        ]}
    }},
    {"$group": {
        "_id": "$c_acctbals.cntrycode",
        "numcust": {"$sum": 1},
        "totacctbal": {"$sum": "$c_acctbals.c_acctbal"}
    }},
    {"$sort": {"_id": 1}}
], allowDiskUse=True)
wall_time = time.time() - t0
print(wall_time*1000)
