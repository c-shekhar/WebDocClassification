from DataIngestion.Feeds import *
from ingestionConfig import *
import sys
# feedToCrawl = sys.argv[1]
# feedToCrawl = "http://feeds.feedburner.com/ndtvmovies-latest"
feedsObject = Feeds(db, FEEDS_COLLECTION_NAME, DATA_COLLECTION_NAME)
feedsObject.getUrlsFromFeed()