from DataIngestion.ndtvFeedSeeder import ndtvFeedsObject
from ingestionConfig import *
import sys
feedToCrawl = sys.argv[1]
ndtvFeedsObject.getUrlsFromFeed(feedToCrawl)