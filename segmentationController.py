import requests
from config import *
from WebPageSegmentation.blockSegmentor import *
from WebPageSegmentation.blockFuse import *
import sys 
#for system encoding. Default should be set to utf-8 for printing purposes. 
reload(sys)
sys.setdefaultencoding('utf-8')

newsUrls = db[DATA_COLLECTION_NAME].find()

def runner(url):
	htmlDoc = requests.get(url['url']).text
	soup = BeautifulSoup(url['html'],"html.parser")
	blockStack = []
	bodyTag = soup.body
	#object for block segmentor
	blockSegmentorObject = BlockSegmentor()
	blockSegmentorObject.getBlockSegments(bodyTag,blockStack)
	structuredBlockDict = blockSegmentorObject.getStructuredBlocks(blockStack)
	#object for block fusion
	blockFusionObject = BlockFusion(MAXIMUM_CHARACTERS, STATEMENT_LENGTH, BOILER_PLATE_THRESHOLD)
	return blockFusionObject.getDoc(structuredBlockDict)


if __name__ == '__main__':
	
	for eachUrl in newsUrls:
		doc = {}
		doc["_id"] = eachUrl['url']
		doc["blocks"] = runner(eachUrl)
		try:
			db[BLOCK_COLLECTION_NAME].insert(doc)
		except Exception as e:
			print e
		