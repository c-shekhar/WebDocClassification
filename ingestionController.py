from DataIngestion.Feeds import *
from config import *
import sys

feedsObject = Feeds(db, FEEDS_COLLECTION_NAME, DATA_COLLECTION_NAME)
feedsObject.getUrlsFromFeed()