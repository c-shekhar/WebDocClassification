import requests
from WebPageSegmentation.blockSegmentor import *
from WebPageSegmentation.blockFuse import *
from config import *

newsUrls = db[DATA_COLLECTION_NAME].find()

def runner(url):
	htmlDoc = requests.get(url).text
	soup = BeautifulSoup(htmlDoc,"html.parser")
	blockStack = []
	bodyTag = soup.body
	#object for block segmentor
	blockSegmentorObject = BlockSegmentor()
	blockSegmentorObject.getBlockSegments(bodyTag,blockStack)
	atomicBlockDict = blockSegmentorObject.getAtomicBlocks(blockStack)
	#object for block fusion
	blockFusionObject = BlockFusion()
	return blockFusionObject.getDoc(atomicBlockDict)

if __name__ == '__main__':
	
	for eachUrl in newsUrls:
		doc = {}
		doc["_id"] = eachUrl['url']
		doc["blocks"] = runner(eachUrl['url'])
		print doc
		try:
			db[BLOCK_COLLECTION_NAME].insert(doc)
		except Exception as e:
			print e
		