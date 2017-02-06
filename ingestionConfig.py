from pymongo import MongoClient

HOST_NAME = "localhost"
PORT_NAME = 27017
CLIENT_OBJECT = MongoClient(HOST_NAME,PORT_NAME)
DATABASE_NAME = "webDocClassification"
db = CLIENT_OBJECT[DATABASE_NAME]
FEEDS_COLLECTION_NAME = "feedsInfo"
DATA_COLLECTION_NAME = "htmlInfo"