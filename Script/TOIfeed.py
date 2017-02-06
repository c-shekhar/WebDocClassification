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
	if feed.getText() in feedsList:
		feedLinks = feedparser.parse(feed['href'])
		feedEntry = {}
		feedEntry['category'] = feed.getText()
		feedEntry['url'] = feed['href']
		feedEntry['_id'] = feedEntry['category'] + '_' + feed['href']
		db[FEEDS_COLLECTION_NAME].insert(feedEntry)
		# entries = feedLinks['entries']
		# if entries:
		# 	for entry in entries:
		# 		for link in entry['links']:
		# 			if not re.match(r'/videos/',link['href']):
						
		# 	 			linkEntry = {}
		# 	 			linkEntry['_id'] = feedEntry['category'] + '_' + link['href']
		# 				linkEntry['category'] = feedEntry['category']
		# 				linkEntry['url'] = link['href']
 	# 					linkEntry['title'] = entry['title']
 	# 					linkEntry['done'] = False
 	# 					linkEntry['feedURL'] = feedEntry['url']
		# 				html = requests.get(link['href']).text
		# 				soup = BeautifulSoup(html,"lxml")
		# 				linkEntry['html'] = str(soup.select('body'))
		# 				try:
		# 					db[HTML_COLLECTION_NAME].insert(linkEntry)
		# 				except Exception as e:
		# 					pass
		# 			else:
		# 				break

			