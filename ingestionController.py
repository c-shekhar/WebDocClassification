from DataIngestion.ndtvFeedSeeder import ndtvFeedsObject
from ingestionConfig import *
import sys
feedToCrawl = sys.argv[1]
# feedToCrawl = "http://feeds.feedburner.com/ndtvmovies-latest"
ndtvFeedsObject.getUrlsFromFeed(feedToCrawl)