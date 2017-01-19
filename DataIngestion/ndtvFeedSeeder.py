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
		if feedToCrawl not in self.crawledFeeds:
			parsedFeed = feedparser.parse(feedLink)
			print parsedFeed['entries']

	def crawlUrl(self, urlToCrawl):
		pass

ndtvFeedsObject = ndtvFeeds(dbObject,feedsCollectionName,dataCollectionName)

@app.task
def runnerCrawlUrl(feedToCrawl):
	ndtvFeedsObject.crawlFeed(feedToCrawl)