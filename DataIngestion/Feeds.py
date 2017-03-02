import feedparser
import requests
import unicodedata
from bs4 import BeautifulSoup
# from celery import Celery
# app = Celery("DataIngestion.ndtvFeedSeeder", broker = "redis://")

class Feeds():
	def __init__(self, dbObject, feedsCollectionName, dataCollectionName):
		self.db = dbObject
		self.feedsCollectionName = feedsCollectionName
		self.dataCollectionName = dataCollectionName
		self.notCrawledFeeds = self.db[self.feedsCollectionName].find({'crawled':False})
	
	def getUrlsFromFeed(self):

		for feedLink in self.notCrawledFeeds:
			print(feedLink)
			feedLinkEntry = {}
			parsedFeed = feedparser.parse(feedLink['url'])

			for eachFeed in parsedFeed['entries']:
				
				feedLinkEntry['_id'] = feedLink['category'] + '_' + eachFeed['link']
				feedLinkEntry['category'] = feedLink['category']
				feedLinkEntry['feedURL'] = feedLink['url']
				feedLinkEntry['url'] = eachFeed['link']
				feedLinkEntry['title'] = eachFeed['title_detail']['value']
				html = requests.get(eachFeed['link']).text
				soup = BeautifulSoup(html,"html.parser")
				feedLinkEntry['html'] = soup.encode()
				feedLinkEntry['source'] = feedLink['source']

				self.db[self.dataCollectionName].insert(feedLinkEntry)
			self.db[self.feedsCollectionName].update({'_id':feedLink['_id']},{'$set':{'crawled':True}}) 
