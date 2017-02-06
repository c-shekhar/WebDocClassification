import feedparser
from bs4 import BeautifulSoup
import requests
# import re
from pymongo import MongoClient

HOST_NAME = "localhost"
PORT_NAME = 27017
CLIENT_OBJECT = MongoClient(HOST_NAME,PORT_NAME)
DATABASE_NAME = "webDocClassification"
db = CLIENT_OBJECT[DATABASE_NAME]
FEEDS_COLLECTION_NAME = "feedsInfo"
DATA_COLLECTION_NAME = "htmlInfo"

#for all the feeds
toiFeedHTML = requests.get('http://timesofindia.indiatimes.com/rss.cms').text
toiSoup = BeautifulSoup(toiFeedHTML,"html.parser")
feeds = toiSoup.find(text='Main Feeds').parent.parent.select('tr td a')
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