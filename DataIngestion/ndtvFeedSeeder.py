from ingestionConfig import *
import feedparser
import requests
from celery import Celery
app = Celery("DataIngestion.ndtvFeedSeeder", broker = "redis://")

class ndtvFeeds():
	def __init__(self, dbObject, feedsCollectionName, dataCollectionName):
		self.db = dbObject
		self.feedsCollectionName = feedsCollectionName
		self.dataCollectionName = dataCollectionName
		self.crawledFeeds = self.db[self.feedsCollectionName].distinct("feedLink")
	
	def getUrlsFromFeed(self, feedLink):
		if feedLink not in self.crawledFeeds:
			parsedFeed = feedparser.parse(feedLink)
			for eachFeed in parsedFeed['entries']:
				print eachFeed,"\n"

	def crawlUrl(self, urlToCrawl):
		pass

ndtvFeedsObject = ndtvFeeds(dbObject,feedsCollectionName,dataCollectionName)

@app.task
def runnerCrawlUrl(feedToCrawl):
	ndtvFeedsObject.crawlFeed(feedToCrawl)