import feedparser
from bs4 import BeautifulSoup
import requests
import re
from pymongo import MongoClient

MONGO_SERVER = 'localhost'
MONGO_PORT = 27017
MONGO_CLIENT_OBJECT = MongoClient(MONGO_SERVER, MONGO_PORT)
DATABASE_NAME = 'feedInfo'
FEEDS_COLLECTION_NAME = 'feeds'
HTML_COLLECTION_NAME = 'newsHTML'
db = MONGO_CLIENT_OBJECT[DATABASE_NAME]

#for all the feeds
toiFeedHTML = requests.get('http://timesofindia.indiatimes.com/rss.cms').text
toiSoup = BeautifulSoup(toiFeedHTML,"lxml")
feeds = toiSoup.select('tr td a')
feedsList = ["Health","Sports","Entertainment","Business","Education","Science","Tech"]
for feed in feeds:
	if feed.getText() in feedsList and 'rssfeedsvideo' not in feed['href']:
		
		feedEntry = {}
		feedEntry['category'] = feed.getText()
		feedEntry['source'] = 'TOI'
		feedEntry['crawled'] = False
		feedEntry['url'] = feed['href']
		feedEntry['_id'] = feedEntry['category'] + '_' + feed['href']
		print(feedEntry)
		db[FEEDS_COLLECTION_NAME].insert(feedEntry)
		

			