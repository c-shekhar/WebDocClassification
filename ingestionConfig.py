from pymongo import MongoClient

hostName = "localhost"
portName = 27017
clientObject = MongoClient(hostName,portName)
dbName = "webDocClassification"
dbObject = clientObject[dbName]
feedsCollectionName = "Feeds"
dataCollectionName = "Data"